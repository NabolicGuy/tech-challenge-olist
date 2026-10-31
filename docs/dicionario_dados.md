# Dicionário de dados

## 1. Tabelas originais do Olist

Arquivos em `data/raw/`, lidos por `olist.data.carregar(nome)`. Os CEPs são convertidos para texto com 5 dígitos (o arquivo original perde o zero à esquerda).

### `orders` · olist_orders_dataset.csv (99.441 linhas)

| Coluna | Descrição |
|---|---|
| `order_id` | Identificador do pedido (chave) |
| `customer_id` | Identificador do cliente **naquele pedido** (muda a cada compra) |
| `order_status` | Status: delivered, shipped, canceled, unavailable, invoiced, processing, created, approved |
| `order_purchase_timestamp` | Data e hora da compra |
| `order_approved_at` | Aprovação do pagamento |
| `order_delivered_carrier_date` | Postagem: entrega do pedido à transportadora |
| `order_delivered_customer_date` | Entrega ao cliente |
| `order_estimated_delivery_date` | Data de entrega prometida ao cliente (sem horário) |

### `customers` · olist_customers_dataset.csv (99.441 linhas)

| Coluna | Descrição |
|---|---|
| `customer_id` | Chave de ligação com `orders` |
| `customer_unique_id` | Identificador da pessoa (permite medir recompra) |
| `customer_zip_code_prefix` | 5 primeiros dígitos do CEP |
| `customer_city`, `customer_state` | Cidade e UF |

### `order_items` · olist_order_items_dataset.csv (112.650 linhas)

| Coluna | Descrição |
|---|---|
| `order_id`, `order_item_id` | Pedido e número sequencial do item (chave composta) |
| `product_id`, `seller_id` | Produto e vendedor |
| `shipping_limit_date` | Data-limite para o vendedor postar o item |
| `price` | Preço do item (R$) |
| `freight_value` | Frete do item (R$) |

### `payments` · olist_order_payments_dataset.csv (103.886 linhas)

| Coluna | Descrição |
|---|---|
| `order_id`, `payment_sequential` | Pedido e sequência do pagamento (um pedido pode ter vários meios) |
| `payment_type` | credit_card, boleto, voucher, debit_card, not_defined |
| `payment_installments` | Número de parcelas |
| `payment_value` | Valor pago (R$) |

### `reviews` · olist_order_reviews_dataset.csv (99.224 linhas)

| Coluna | Descrição |
|---|---|
| `review_id`, `order_id` | Avaliação e pedido (chave composta) |
| `review_score` | Nota de 1 a 5 |
| `review_comment_title`, `review_comment_message` | Título e comentário (opcionais) |
| `review_creation_date`, `review_answer_timestamp` | Envio da pesquisa e resposta do cliente |

### `products` · olist_products_dataset.csv (32.951 linhas)

| Coluna | Descrição |
|---|---|
| `product_id` | Produto (chave) |
| `product_category_name` | Categoria em português |
| `product_name_lenght`, `product_description_lenght` | Tamanho do nome e da descrição (grafia original do dataset) |
| `product_photos_qty` | Número de fotos |
| `product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm` | Peso e dimensões |

### `sellers` · olist_sellers_dataset.csv (3.095 linhas)

| Coluna | Descrição |
|---|---|
| `seller_id` | Vendedor (chave) |
| `seller_zip_code_prefix`, `seller_city`, `seller_state` | CEP, cidade e UF |

### `geolocation` · olist_geolocation_dataset.csv (1.000.163 linhas)

Coordenadas por prefixo de CEP (vários pontos por CEP). **Não usada nas métricas** (ver governança).

### `category_translation` · product_category_name_translation.csv (71 linhas)

Tradução das categorias para inglês. Os relatórios usam os nomes em português, com acentuação ajustada em `olist.prep.NOMES_CATEGORIAS`.

## 2. Base analítica de pedidos

Gerada por `olist.prep.carregar_base_pedidos()` e salva em `data/processed/base_pedidos.parquet`. Uma linha por pedido da janela de análise (jan/2017 a ago/2018, 99.092 pedidos). Inclui todas as colunas de `orders` e `customers` e mais:

| Coluna | Definição |
|---|---|
| `n_itens`, `n_sellers`, `n_categorias` | Quantidade de itens, vendedores e categorias no pedido |
| `valor_produtos`, `valor_frete` | Soma de `price` e de `freight_value` dos itens |
| `gmv` | Receita do pedido = `valor_produtos` + `valor_frete` |
| `perc_frete` | `valor_frete` / `gmv` |
| `peso_total_g` | Peso somado dos itens |
| `categoria`, `seller_id`, `seller_state` | Categoria, vendedor e UF do vendedor do **item de maior valor** |
| `valor_pago`, `parcelas` | Soma dos pagamentos e maior número de parcelas |
| `meio_pagamento` | Meio de pagamento de maior valor no pedido |
| `review_score`, `review_comment_title`, `review_comment_message` | Avaliação mais recente do pedido |
| `tem_comentario` | Se a avaliação tem comentário |
| `mes` | Primeiro dia do mês da compra |
| `regiao`, `regiao_seller` | Região do cliente e do vendedor |
| `mesma_uf` | Cliente e vendedor no mesmo estado |
| `valido` | Pedido conta para receita: não está cancelado nem indisponível e tem itens |
| `entregue` | Status `delivered` e com data de entrega |
| `dias_aprovacao` | Compra → aprovação do pagamento |
| `dias_postagem` | Aprovação → postagem (tempo do vendedor) |
| `dias_transporte` | Postagem → entrega (tempo da transportadora) |
| `dias_entrega` | Compra → entrega (prazo total) |
| `dias_prometidos` | Compra → data prometida |
| `dias_atraso` | Dia da entrega − data prometida (negativo = adiantado) |
| `atrasado` | 1 se entregue em dia posterior ao prometido; 0 se no prazo; vazio se não entregue |
| `nota_baixa` | 1 se nota 1 ou 2; 0 se 3 a 5; vazio se sem avaliação |

`olist.prep.base_itens()` gera a base equivalente por item, com categoria, UF do vendedor e do cliente e data da compra.

## 3. Fontes externas

Arquivos em `data/external/`, gerados por `scripts/baixar_dados.py`.

| Arquivo | Colunas | Fonte |
|---|---|---|
| `populacao_uf_2018.csv` | `uf`, `populacao` | IBGE, SIDRA tabela 6579: população residente estimada em 2018 |
| `pib_uf_2018.csv` | `uf`, `pib_mil_reais` | IBGE, SIDRA tabela 5938: PIB a preços correntes em 2018, em mil reais |
| `ipca_mensal.csv` | `mes`, `ipca_pct` | Banco Central, SGS série 433: variação mensal do IPCA em % (2016–2018) |
