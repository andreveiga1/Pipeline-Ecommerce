{{ config(materialized='table') }}

WITH vendas_mensais AS (
    SELECT 
        DATE_TRUNC('month', CAST(data_venda AS DATE)) AS mes_venda,
        SUM(quantidade * preco_unitario) AS receita_total,
        SUM(quantidade) AS quantidade_total,
        COUNT(DISTINCT id_venda) AS total_vendas,
        COUNT(DISTINCT id_cliente) AS total_clientes_unicos
    FROM {{ ref('silver_vendas') }}
    GROUP BY 1
)

SELECT
    mes_venda,
    receita_total,
    quantidade_total,
    total_vendas,
    total_clientes_unicos,
    -- Analisando o crescimento da receita em relação ao mês anterior
    LAG(receita_total) OVER (ORDER BY mes_venda) AS receita_mes_anterior,
    (receita_total - LAG(receita_total) OVER (ORDER BY mes_venda)) AS crescimento_receita_absoluto,
    ROUND(
        CAST(
            (receita_total - LAG(receita_total) OVER (ORDER BY mes_venda)) / 
            NULLIF(LAG(receita_total) OVER (ORDER BY mes_venda), 0) * 100 
            AS NUMERIC
        )
    , 2) AS crescimento_receita_percentual
FROM vendas_mensais
ORDER BY mes_venda DESC
