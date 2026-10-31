"""Construção das bases analíticas: uma linha por item e uma linha por pedido."""
import numpy as np
import pandas as pd

from . import config
from .data import carregar_todas

CACHE_PEDIDOS = config.DATA_PROCESSED / "base_pedidos.parquet"


# Nomes com acentuação para as categorias mais relevantes; as demais são só formatadas
NOMES_CATEGORIAS = {
    "agro_industria_e_comercio": "Agroindústria e comércio",
    "alimentos": "Alimentos",
    "artes": "Artes",
    "audio": "Áudio",
    "automotivo": "Automotivo",
    "bebes": "Bebês",
    "bebidas": "Bebidas",
    "beleza_saude": "Beleza e saúde",
    "brinquedos": "Brinquedos",
    "cama_mesa_banho": "Cama, mesa e banho",
    "casa_conforto": "Casa e conforto",
    "casa_construcao": "Casa e construção",
    "climatizacao": "Climatização",
    "consoles_games": "Consoles e games",
    "construcao_ferramentas_construcao": "Ferramentas de construção",
    "cool_stuff": "Cool stuff",
    "eletrodomesticos": "Eletrodomésticos",
    "eletrodomesticos_2": "Eletrodomésticos 2",
    "eletronicos": "Eletrônicos",
    "eletroportateis": "Eletroportáteis",
    "esporte_lazer": "Esporte e lazer",
    "fashion_bolsas_e_acessorios": "Bolsas e acessórios",
    "fashion_calcados": "Calçados",
    "fashion_roupa_feminina": "Moda feminina",
    "fashion_roupa_masculina": "Moda masculina",
    "fashion_underwear_e_moda_praia": "Moda íntima e praia",
    "ferramentas_jardim": "Ferramentas e jardim",
    "informatica_acessorios": "Informática e acessórios",
    "instrumentos_musicais": "Instrumentos musicais",
    "livros_interesse_geral": "Livros",
    "malas_acessorios": "Malas e acessórios",
    "market_place": "Marketplace",
    "moveis_cozinha_area_de_servico_jantar_e_jardim": "Móveis de cozinha e jardim",
    "moveis_decoracao": "Móveis e decoração",
    "moveis_escritorio": "Móveis de escritório",
    "moveis_quarto": "Móveis de quarto",
    "moveis_sala": "Móveis de sala",
    "papelaria": "Papelaria",
    "pcs": "Computadores",
    "perfumaria": "Perfumaria",
    "pet_shop": "Pet shop",
    "relogios_presentes": "Relógios e presentes",
    "sem_categoria": "Sem categoria",
    "sinalizacao_e_seguranca": "Sinalização e segurança",
    "telefonia": "Telefonia",
    "telefonia_fixa": "Telefonia fixa",
    "utilidades_domesticas": "Utilidades domésticas",
}


def nome_categoria(s: pd.Series) -> pd.Series:
    """'cama_mesa_banho' -> 'Cama, mesa e banho'; categorias fora do dicionário só perdem o '_'."""
    s = s.fillna("sem_categoria")
    return s.map(NOMES_CATEGORIAS).fillna(s.str.replace("_", " ").str.capitalize())


def no_periodo(datas: pd.Series, inicio: str, fim: str) -> pd.Series:
    """True para datas entre `inicio` e o fim do dia `fim` (inclusive)."""
    return (datas >= pd.Timestamp(inicio)) & (datas < pd.Timestamp(fim) + pd.Timedelta(days=1))


def review_por_pedido(reviews: pd.DataFrame) -> pd.DataFrame:
    # Alguns pedidos têm mais de uma avaliação: fica a resposta mais recente
    r = reviews.sort_values("review_answer_timestamp").drop_duplicates("order_id", keep="last")
    r = r.assign(tem_comentario=r["review_comment_message"].notna())
    return r[["order_id", "review_score", "review_comment_title", "review_comment_message", "tem_comentario"]]


def base_itens(t: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Itens com categoria, atributos do produto, UF do vendedor e dados do pedido."""
    produtos = t["products"][["product_id", "product_category_name", "product_weight_g", "product_photos_qty"]]
    itens = (
        t["order_items"]
        .merge(produtos, on="product_id", how="left")
        .merge(t["sellers"][["seller_id", "seller_state", "seller_city"]], on="seller_id", how="left")
        .merge(
            t["orders"][["order_id", "customer_id", "order_status", "order_purchase_timestamp"]],
            on="order_id",
            how="left",
        )
        .merge(t["customers"][["customer_id", "customer_unique_id", "customer_state"]], on="customer_id", how="left")
    )
    itens["categoria"] = nome_categoria(itens["product_category_name"])
    itens["mes"] = itens["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    itens["valido"] = ~itens["order_status"].isin(config.STATUS_INVALIDOS)
    return itens


def base_pedidos(t: dict[str, pd.DataFrame] | None = None, somente_janela: bool = True) -> pd.DataFrame:
    """Uma linha por pedido com valores, prazos, pagamento, avaliação e localização."""
    t = t or carregar_todas()
    itens = base_itens(t)

    resumo_itens = itens.groupby("order_id").agg(
        n_itens=("order_item_id", "size"),
        n_sellers=("seller_id", "nunique"),
        n_categorias=("categoria", "nunique"),
        valor_produtos=("price", "sum"),
        valor_frete=("freight_value", "sum"),
        peso_total_g=("product_weight_g", "sum"),
    )
    # Item mais caro define a categoria e o vendedor "principal" do pedido
    principal = (
        itens.sort_values(["order_id", "price"], ascending=[True, False])
        .drop_duplicates("order_id")[["order_id", "categoria", "seller_id", "seller_state"]]
    )

    pag = t["payments"]
    resumo_pag = pag.groupby("order_id").agg(valor_pago=("payment_value", "sum"), parcelas=("payment_installments", "max"))
    meio_principal = (
        pag.sort_values(["order_id", "payment_value"], ascending=[True, False])
        .drop_duplicates("order_id")[["order_id", "payment_type"]]
        .rename(columns={"payment_type": "meio_pagamento"})
    )

    df = (
        t["orders"]
        .merge(t["customers"], on="customer_id", how="left")
        .merge(resumo_itens, on="order_id", how="left")
        .merge(principal, on="order_id", how="left")
        .merge(resumo_pag, on="order_id", how="left")
        .merge(meio_principal, on="order_id", how="left")
        .merge(review_por_pedido(t["reviews"]), on="order_id", how="left")
    )

    df["gmv"] = df["valor_produtos"] + df["valor_frete"]
    df["perc_frete"] = df["valor_frete"] / df["gmv"]
    df["mes"] = df["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    df["regiao"] = df["customer_state"].map(config.UF_REGIAO)
    df["regiao_seller"] = df["seller_state"].map(config.UF_REGIAO)
    df["mesma_uf"] = df["customer_state"] == df["seller_state"]
    # Pedido válido para receita: não cancelado/indisponível e com itens registrados
    df["valido"] = ~df["order_status"].isin(config.STATUS_INVALIDOS) & df["n_itens"].notna()
    df["entregue"] = df["order_status"].eq("delivered") & df["order_delivered_customer_date"].notna()

    def dias(inicio: str, fim: str) -> pd.Series:
        return (df[fim] - df[inicio]).dt.total_seconds() / 86400

    df["dias_aprovacao"] = dias("order_purchase_timestamp", "order_approved_at")
    df["dias_postagem"] = dias("order_approved_at", "order_delivered_carrier_date")
    df["dias_transporte"] = dias("order_delivered_carrier_date", "order_delivered_customer_date")
    df["dias_entrega"] = dias("order_purchase_timestamp", "order_delivered_customer_date")
    df["dias_prometidos"] = dias("order_purchase_timestamp", "order_estimated_delivery_date")
    # O prazo estimado é uma data sem hora: atraso = entregue em dia posterior ao prometido
    df["dias_atraso"] = (df["order_delivered_customer_date"].dt.normalize() - df["order_estimated_delivery_date"]).dt.days
    df["atrasado"] = np.where(df["entregue"], (df["dias_atraso"] > 0).astype(float), np.nan)
    df["nota_baixa"] = np.where(df["review_score"].notna(), (df["review_score"] <= 2).astype(float), np.nan)

    if somente_janela:
        df = df[no_periodo(df["order_purchase_timestamp"], config.INICIO_JANELA, config.FIM_JANELA)]
    return df.reset_index(drop=True)


def carregar_base_pedidos(recriar: bool = False) -> pd.DataFrame:
    """Base de pedidos da janela de análise, com cache em data/processed."""
    if CACHE_PEDIDOS.exists() and not recriar:
        return pd.read_parquet(CACHE_PEDIDOS)
    df = base_pedidos()
    CACHE_PEDIDOS.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CACHE_PEDIDOS, index=False)
    return df
