{% macro add_bidirectional_rankings(relation, partition_by_columns, order_by_column, asc_rank_alias='rn_asc', desc_rank_alias='rn_desc') %}
SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY {{ partition_by_columns | join(', ') }} ORDER BY {{ order_by_column }} ASC) AS {{ asc_rank_alias }},
    ROW_NUMBER() OVER (PARTITION BY {{ partition_by_columns | join(', ') }} ORDER BY {{ order_by_column }} DESC) AS {{ desc_rank_alias }}
FROM {{ relation }}
{% endmacro %}