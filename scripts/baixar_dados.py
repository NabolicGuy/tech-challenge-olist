"""Baixa o dataset do Olist (Kaggle) e as fontes externas (IBGE e Banco Central).

Uso, a partir da raiz do projeto:
    python scripts/baixar_dados.py            # baixa só o que ainda não existe
    python scripts/baixar_dados.py --forcar   # baixa tudo de novo
"""
import argparse
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from olist.config import DATA_EXTERNAL, DATA_RAW, KAGGLE_URL, UF_CODIGO_IBGE  # noqa: E402
from olist.data import ARQUIVOS  # noqa: E402

SIDRA_POPULACAO = "https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/9324/p/2018"
SIDRA_PIB = "https://apisidra.ibge.gov.br/values/t/5938/n3/all/v/37/p/2018"
BCB_IPCA = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=01/01/2016&dataFinal=31/12/2018"


def baixar(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return resp.read()


def baixar_olist(forcar: bool) -> None:
    if not forcar and all((DATA_RAW / f).exists() for f in ARQUIVOS.values()):
        print("Olist: arquivos já existem em data/raw")
        return
    print("Olist: baixando do Kaggle (~45 MB)...")
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(baixar(KAGGLE_URL))) as z:
        z.extractall(DATA_RAW)
    print(f"Olist: {len(ARQUIVOS)} arquivos em data/raw")


def _sidra(url: str, coluna: str) -> pd.DataFrame:
    linhas = json.loads(baixar(url))[1:]  # a primeira linha é o cabeçalho descritivo
    df = pd.DataFrame({"uf": [UF_CODIGO_IBGE[int(r["D1C"])] for r in linhas], coluna: [float(r["V"]) for r in linhas]})
    return df.sort_values("uf").reset_index(drop=True)


def baixar_externos(forcar: bool) -> None:
    DATA_EXTERNAL.mkdir(parents=True, exist_ok=True)
    alvos = {
        "populacao_uf_2018.csv": lambda: _sidra(SIDRA_POPULACAO, "populacao"),
        "pib_uf_2018.csv": lambda: _sidra(SIDRA_PIB, "pib_mil_reais"),
        "ipca_mensal.csv": lambda: pd.DataFrame(
            [{"mes": pd.to_datetime(r["data"], dayfirst=True), "ipca_pct": float(r["valor"])} for r in json.loads(baixar(BCB_IPCA))]
        ),
    }
    for arquivo, obter in alvos.items():
        caminho = DATA_EXTERNAL / arquivo
        if caminho.exists() and not forcar:
            print(f"Externo: {arquivo} já existe")
            continue
        obter().to_csv(caminho, index=False)
        print(f"Externo: {arquivo} salvo")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--forcar", action="store_true", help="baixa novamente mesmo que os arquivos existam")
    args = parser.parse_args()
    baixar_olist(args.forcar)
    baixar_externos(args.forcar)
