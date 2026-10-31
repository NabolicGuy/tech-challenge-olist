"""Leitura das tabelas originais do Olist e das fontes externas, com tipos corretos."""
import pandas as pd

from .config import DATA_EXTERNAL, DATA_RAW

ARQUIVOS = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

COLUNAS_DATA = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "reviews": ["review_creation_date", "review_answer_timestamp"],
}


def carregar(nome: str) -> pd.DataFrame:
    """Lê uma tabela do Olist pelo nome curto (ex.: 'orders')."""
    caminho = DATA_RAW / ARQUIVOS[nome]
    if not caminho.exists():
        raise FileNotFoundError(f"{caminho} não encontrado. Rode `python scripts/baixar_dados.py` na raiz do projeto.")
    df = pd.read_csv(caminho, parse_dates=COLUNAS_DATA.get(nome, []))
    # O CEP vem como inteiro e perde o zero à esquerda (01001 -> 1001)
    for col in df.columns:
        if col.endswith("zip_code_prefix"):
            df[col] = df[col].astype(str).str.zfill(5)
    return df


def carregar_todas(incluir_geolocalizacao: bool = False) -> dict[str, pd.DataFrame]:
    """Lê todas as tabelas. A geolocalização (1 milhão de linhas) só entra se pedida."""
    nomes = [n for n in ARQUIVOS if incluir_geolocalizacao or n != "geolocation"]
    return {nome: carregar(nome) for nome in nomes}


def carregar_populacao_uf() -> pd.DataFrame:
    """População residente estimada por UF em 2018 (IBGE, tabela SIDRA 6579)."""
    return pd.read_csv(DATA_EXTERNAL / "populacao_uf_2018.csv")


def carregar_pib_uf() -> pd.DataFrame:
    """PIB a preços correntes por UF em 2018, em mil reais (IBGE, tabela SIDRA 5938)."""
    return pd.read_csv(DATA_EXTERNAL / "pib_uf_2018.csv")


def carregar_ipca() -> pd.DataFrame:
    """Variação mensal do IPCA em % (Banco Central, série SGS 433)."""
    return pd.read_csv(DATA_EXTERNAL / "ipca_mensal.csv", parse_dates=["mes"])
