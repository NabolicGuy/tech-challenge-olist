# Governança, qualidade e reprodutibilidade

O diagnóstico completo, com o código que gera cada número, está no [notebook 01](../notebooks/01_qualidade_dados.ipynb).

## 1. Diagnóstico da base

| Verificação | Resultado |
|---|---|
| Chaves primárias | Únicas em todas as tabelas (pedido, item, pagamento, avaliação, produto, vendedor) |
| Pedidos sem itens | 775 (0,8%), quase todos indisponíveis ou cancelados |
| Pedidos sem avaliação | 768 (0,8%) |
| Pedidos com mais de uma avaliação | 547 (0,6%) |
| Produtos sem categoria | 610 (1,9% dos produtos) |
| Valor pago vs. preço + frete | Batem (diferença de até R$ 1) em 99,7% dos pedidos com itens |
| Postagem registrada antes da aprovação | 1.359 pedidos (1,4%) |
| Entrega registrada antes da postagem | 23 pedidos |
| Geolocalização | 1 milhão de linhas para 19 mil CEPs, com 42 coordenadas fora do Brasil |
| Cobertura temporal | set/2016 a out/2018, mas fluxo regular só de jan/2017 a 21/08/2018 |

## 2. Decisões de tratamento

| Decisão | Motivo |
|---|---|
| Janela de análise de jan/2017 a ago/2018 | 2016 foi uma fase inicial (sem vendas em nov/2016) e após ago/2018 restam ~20 pedidos residuais. Ficam fora 349 pedidos (0,4%). |
| Séries mensais até jul/2018; série diária até 21/08/2018 | O volume despenca de ~250 para quase zero pedidos/dia entre 22 e 31/08/2018, sinal de corte na extração. Para ago/2018 usamos o ritmo diário dos dias 1 a 21. |
| Receita (GMV) = preço + frete dos itens | Há pagamentos registrados em pedidos sem itens (indisponíveis), que não representam venda. |
| Cancelados e indisponíveis fora da receita | Não geraram venda (1.234 pedidos). |
| Uma avaliação por pedido | Mantida a resposta mais recente quando há mais de uma. |
| Cliente = `customer_unique_id` | O `customer_id` muda a cada pedido; usá-lo esconderia a recompra (3.345 IDs consolidados). |
| Recompra = compra em dia diferente | Evita contar como recompra um carrinho dividido em vários pedidos no mesmo momento. |
| Atraso = entrega em dia posterior à data prometida | A data prometida não tem horário; o critério não conta como atraso a entrega no próprio dia. |
| Categoria e vendedor do pedido = item de maior valor | 9,9% dos pedidos têm mais de um item. |
| Etapas do prazo com duração negativa descartadas | Só na decomposição do prazo (notebook 03); o prazo total não é afetado. |
| Rotas com menos de 30 pedidos não exibidas | Médias com poucos casos não são confiáveis (notebook 03). |
| Coordenadas geográficas não usadas | UF e cidade já vêm nas tabelas de clientes e vendedores. |

## 3. Reprodutibilidade

- **Ambiente:** Python 3.12 com as versões fixadas em `requirements.txt`.
- **Dados:** `scripts/baixar_dados.py` baixa o dataset do Kaggle e as séries externas. As séries externas estão versionadas em `data/external/` para que a análise não dependa da disponibilidade das APIs.
- **Regras centralizadas:** janela, status válidos e definições de negócio ficam em `src/olist/config.py` e `src/olist/prep.py`. Nenhum notebook redefine essas regras.
- **Execução:** `jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb` executa tudo do zero. Os notebooks são determinísticos e salvam os gráficos em `reports/figures/`.
- **Números no texto:** as conclusões citam valores impressos pelas próprias células, e os títulos dos gráficos são calculados a partir dos dados.

## 4. Limitações

- O dataset é uma **amostra pública e anonimizada**, que pode não representar 100% do volume da empresa. Taxas e proporções são mais robustas que os valores absolutos.
- As avaliações refletem só os clientes que responderam à pesquisa (99% dos pedidos têm nota, mas só 41% têm comentário).
- A recompra é medida dentro de uma janela de 20 meses. Clientes recentes tiveram menos tempo para voltar; por isso a análise de recompra por experiência usa uma janela fixa de 180 dias.
- A projeção do notebook 06 supõe que a operação não muda e estima o efeito da Black Friday a partir de um único evento (2017).
- Os impactos das recomendações (notebook 07) são estimativas de ordem de grandeza para priorizar ações, não substituem pilotos controlados.
