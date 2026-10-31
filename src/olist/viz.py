"""Identidade visual dos gráficos, formatação em pt-BR e exportação de figuras."""
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize

from .config import FIGURES

CORES = {
    "principal": "#1F4E79",
    "secundaria": "#5B9BD5",
    "destaque": "#E07B39",
    "neutro": "#A6A6A6",
    "positivo": "#2E8B57",
    "negativo": "#C0392B",
    "texto": "#262626",
    "subtexto": "#6B6B6B",
}
CORES_REGIAO = {
    "Sudeste": "#1F4E79",
    "Sul": "#5B9BD5",
    "Centro-Oeste": "#70AD47",
    "Nordeste": "#E07B39",
    "Norte": "#C0392B",
}

# Grade aproximada do mapa do Brasil (coluna, linha): norte em cima, Nordeste à direita
GRADE_UF = {
    "RR": (1, 0), "AP": (3, 0),
    "AM": (0, 1), "PA": (2, 1), "MA": (3, 1), "CE": (4, 1), "RN": (5, 1),
    "AC": (0, 2), "RO": (1, 2), "MT": (2, 2), "TO": (3, 2), "PI": (4, 2), "PB": (5, 2),
    "MS": (1, 3), "GO": (2, 3), "DF": (3, 3), "BA": (4, 3), "PE": (5, 3),
    "SP": (1, 4), "MG": (2, 4), "ES": (3, 4), "SE": (4, 4), "AL": (5, 4),
    "PR": (1, 5), "RJ": (2, 5),
    "SC": (1, 6),
    "RS": (1, 7),
}


def aplicar_estilo() -> None:
    plt.rcParams.update({
        "figure.figsize": (11, 5),
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "font.size": 11,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlepad": 28,
        "axes.labelcolor": CORES["subtexto"],
        "axes.edgecolor": "#BFBFBF",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": "#E7E7E7",
        "xtick.color": CORES["subtexto"],
        "ytick.color": CORES["subtexto"],
        "legend.frameon": False,
        "text.color": CORES["texto"],
    })
    pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
    pd.set_option("display.max_colwidth", None)


def _br(x: float, casas: int) -> str:
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def num(x: float, casas: int = 0) -> str:
    """96478 -> '96.478'."""
    return _br(x, casas)


def pct(x: float, casas: int = 1) -> str:
    """0.0677 -> '6,8%'."""
    return f"{_br(x * 100, casas)}%"


def brl(x: float, casas: int = 1) -> str:
    """Valor em reais abreviado: 'R$ 13,6 mi', 'R$ 350 mil', 'R$ 154'."""
    if abs(x) >= 1e9:
        return f"R$ {_br(x / 1e9, casas)} bi"
    if abs(x) >= 1e6:
        return f"R$ {_br(x / 1e6, casas)} mi"
    if abs(x) >= 1e3:
        return f"R$ {_br(x / 1e3, 0)} mil"
    return f"R$ {_br(x, 0)}"


MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def mes_ano(data) -> str:
    """Timestamp -> 'nov/17'."""
    return f"{MESES[data.month - 1]}/{data:%y}"


eixo_brl = mticker.FuncFormatter(lambda x, _: brl(x))
eixo_pct = mticker.FuncFormatter(lambda x, _: pct(x, 0))
eixo_num = mticker.FuncFormatter(lambda x, _: num(x))
eixo_mes = mticker.FuncFormatter(lambda x, _: mes_ano(mdates.num2date(x)))


def titulo(ax, mensagem: str, subtitulo: str | None = None) -> None:
    """Título com a mensagem principal e subtítulo explicativo em cinza."""
    ax.set_title(mensagem)
    if subtitulo:
        ax.text(0, 1.02, subtitulo, transform=ax.transAxes, color=CORES["subtexto"], fontsize=11, va="bottom")


def fonte(fig, texto: str = "Fonte: Olist, pedidos de jan/2017 a ago/2018") -> None:
    fig.text(0.01, -0.02, texto, color=CORES["subtexto"], fontsize=9, ha="left")


def salvar(fig, nome: str) -> None:
    """Exporta a figura em reports/figures para uso na apresentação."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / f"{nome}.png", bbox_inches="tight", facecolor="white")


def mapa_uf(valores: pd.Series, ax=None, cmap: str = "RdYlGn_r", formato=None, vmin=None, vmax=None, barra: str = ""):
    """Mapa em grade do Brasil: um quadrado por UF colorido pelo valor."""
    formato = formato or (lambda v: _br(v, 1))
    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 8))
    norm = Normalize(vmin=valores.min() if vmin is None else vmin, vmax=valores.max() if vmax is None else vmax)
    paleta = plt.get_cmap(cmap)
    for uf, (col, lin) in GRADE_UF.items():
        v = valores.get(uf, np.nan)
        cor = "#EEEEEE" if pd.isna(v) else paleta(norm(v))
        ax.add_patch(plt.Rectangle((col, -lin), 0.94, 0.94, color=cor, ec="white"))
        luminancia = 1 if pd.isna(v) else 0.299 * cor[0] + 0.587 * cor[1] + 0.114 * cor[2]
        cor_texto = CORES["texto"] if luminancia > 0.55 else "white"
        ax.text(col + 0.47, -lin + 0.6, uf, ha="center", va="center", fontsize=11, fontweight="bold", color=cor_texto)
        ax.text(col + 0.47, -lin + 0.3, "–" if pd.isna(v) else formato(v), ha="center", va="center", fontsize=8.5, color=cor_texto)
    ax.set_xlim(-0.1, 6.1)
    ax.set_ylim(-7.1, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
    if barra:
        sm = plt.cm.ScalarMappable(cmap=paleta, norm=norm)
        cb = plt.colorbar(sm, ax=ax, fraction=0.035, pad=0.01)
        cb.set_label(barra)
        cb.outline.set_visible(False)
    return ax
