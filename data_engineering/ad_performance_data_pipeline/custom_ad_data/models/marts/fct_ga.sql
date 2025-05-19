{{ config(
    unique_key = ['day', 'utm_source', 'utm_medium', 'utm_campaign', '']
) }}

WITH criteo AS (
    SELECT
        *
    FROM
        {{ ref('stg_ga') }}
)
SELECT
    *
FROM
    criteo

{% if is_incremental() %}
    WHERE day > (SELECT MAX(day) FROM {{ this }})
{% endif %}