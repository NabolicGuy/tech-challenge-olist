# Tech Challenge Fase 1 · E-commerce Olist

Relatório analítico para investidores e acionistas, construído sobre o [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): cerca de 100 mil pedidos feitos entre 2016 e 2018 em marketplaces brasileiros. O objetivo é transformar os dados transacionais em uma leitura clara de **crescimento**, **eficiência logística** e **satisfação do cliente**, com recomendações acionáveis e uma projeção para o fim de 2018.

## Resumo executivo

**A tese:** a operação cresce rápido e de forma saudável, mas a **entrega é o gargalo de valor**. O atraso é o que mais destrói a satisfação, e a recompra é quase nula. Corrigir a logística fora de SP e a qualidade dos vendedores é a alavanca mais barata para sustentar o crescimento.

| | |
|---|---|
| **Crescimento** | Receita de jan–jul/2018 **+161%** sobre 2017 (+153% acima da inflação), puxada por volume com ticket estável (~R$ 160). Depois da greve dos caminhoneiros e da Copa, agosto/2018 bateu o recorde de **273 pedidos/dia**. |
| **Projeção** | Mantido o ritmo atual, 2018 fecha com cerca de **R$ 14,3 milhões** (faixa de R$ 13,0 a 15,5 mi), **o dobro de 2017**, com pico de 9,5 mil pedidos na Black Friday. |
| **Logística** | Entrega média de 12,5 dias, com **6,8% de atrasos**. O transporte consome 74% do prazo. Norte e Nordeste esperam até 3x mais que SP; em Alagoas, 21,5% dos pedidos atrasam. |
| **Satisfação** | Nota média de 4,09. Um atraso derruba a nota de **4,3 para 2,3** e multiplica por 6,7 a chance de nota 1–2. Atrasos e não entregas são 9% dos pedidos e **43% das notas baixas**. |
| **Clientes** | **97,8% compram uma única vez.** Clientes de alto valor que compraram só uma vez geram 57% da receita. |
| **Concentração** | O Sudeste tem 65% da receita e 42% da população; 84% dos pedidos saem do Sudeste. Só 5% dos pedidos do Nordeste são atendidos por vendedores locais. |

**Recomendações priorizadas** (impacto estimado sobre os últimos 12 meses):

1. **Plano de choque logístico em RJ e Nordeste.** Levar cada estado à taxa de atraso de SP evitaria cerca de 2.400 atrasos e 1.300 notas 1–2 por ano.
2. **Programa de qualidade de vendedores.** 84 vendedores críticos geram 27% das notas baixas com 17% da receita.
3. **Oferta local no Norte e Nordeste.** Até R$ 2,5 milhões/ano (+21%) se as regiões atingirem a penetração do Centro-Oeste.
4. **Consolidar entregas de pedidos com vários vendedores,** que têm 3,9x mais chance de nota baixa.
5. **CRM de recompra:** cada ponto percentual de recompra vale cerca de R$ 114 mil por ano.
6. **Só encurtar o prazo prometido depois de reduzir a cauda de entregas lentas.** A promessa parece folgada na média, mas 5% das entregas já passam dela.

## Estrutura do repositório

```
├── data/
│   ├── raw/            # CSVs do Olist (baixados pelo script; fora do git)
│   ├── external/       # IBGE (população e PIB por UF) e Banco Central (IPCA)
│   └── processed/      # base analítica em parquet (gerada; fora do git)
├── docs/
│   ├── dicionario_dados.md
│   └── governanca.md
├── notebooks/          # análises, na ordem de leitura
├── reports/figures/    # gráficos exportados para a apresentação
├── scripts/
│   └── baixar_dados.py
├── src/olist/          # funções compartilhadas pelos notebooks
│   ├── config.py       # caminhos, janela de análise e constantes
│   ├── data.py         # leitura das tabelas com tipos corretos
│   ├── prep.py         # bases analíticas (por pedido e por item)
│   └── viz.py          # identidade visual e formatação pt-BR
└── requirements.txt
```

## Notebooks

| Notebook | Pergunta de negócio |
|---|---|
| [01 · Qualidade dos dados](notebooks/01_qualidade_dados.ipynb) | Os dados são confiáveis? Que recortes e tratamentos são necessários? |
| [02 · Crescimento e receita](notebooks/02_crescimento_receita.ipynb) | O negócio cresce? De quais categorias, regiões e vendedores vem a receita? |
| [03 · Logística e SLA](notebooks/03_logistica_sla.ipynb) | A operação entrega no prazo? Onde estão os gargalos? |
| [04 · Clientes e pagamentos](notebooks/04_clientes_pagamentos.ipynb) | O cliente volta? Quem são os mais valiosos e como pagam? |
| [05 · Satisfação](notebooks/05_satisfacao.ipynb) | O que mais pesa na nota do cliente? |
| [06 · Previsão](notebooks/06_previsao.ipynb) | Quanto a operação deve vender até dez/2018? |
| [07 · Oportunidades](notebooks/07_oportunidades_recomendacoes.ipynb) | Onde estão as alavancas de valor e quanto cada uma vale? |

Cada notebook abre com um bloco de **principais conclusões** e termina com os gráficos exportados para `reports/figures/`.

## Como reproduzir

Requer Python 3.12.

```bash
pip install -r requirements.txt
python scripts/baixar_dados.py
jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
```

O script baixa o dataset do Kaggle (download público, sem login) e as séries externas do IBGE e do Banco Central. As séries externas já estão versionadas em `data/external/`, então o script só as baixa de novo com `--forcar`. Os notebooks devem rodar na ordem: o 01 gera a base analítica usada pelos demais (que também é recriada automaticamente se não existir).

## Fontes de dados

| Fonte | Uso |
|---|---|
| [Olist · Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (licença CC BY-NC-SA 4.0) | Pedidos, itens, pagamentos, avaliações, clientes, vendedores e produtos |
| [IBGE · SIDRA, tabela 6579](https://sidra.ibge.gov.br/tabela/6579) | População estimada por UF em 2018 (penetração) |
| [IBGE · SIDRA, tabela 5938](https://sidra.ibge.gov.br/tabela/5938) | PIB por UF em 2018 (renda per capita) |
| [Banco Central · SGS, série 433](https://www3.bcb.gov.br/sgspub/) | IPCA mensal (crescimento real) |
| Calendário | Black Friday (24/11/2017 e 23/11/2018), greve dos caminhoneiros (21/05 a 03/06/2018) e Copa do Mundo (14/06 a 15/07/2018) |

## Governança

- [Dicionário de dados](docs/dicionario_dados.md): tabelas originais, base analítica e fontes externas.
- [Governança e qualidade](docs/governanca.md): diagnóstico da base, decisões de tratamento, janela de análise e limitações.

Todas as regras de negócio (janela, status válidos, definição de atraso, identidade do cliente) ficam em `src/olist/config.py` e `src/olist/prep.py`, para que os notebooks usem exatamente a mesma base.

## Entregáveis

- Repositório: este projeto
- Apresentação executiva: [Google Slides](https://docs.google.com/presentation/d/1M94O8P25V-u7tfDJeuLQOqkt9C7r27lp/edit?usp=sharing)
- Vídeo executivo (até 5 min): *link a incluir*

