{{ config(
    unique_key = ['day', 'campaign', 'adgroup']
) }}

WITH criteo AS (
    SELECT
        *
    FROM
        {{ ref('stg_yahoo') }}
)
SELECT
    *
FROM
    criteo

{% if is_incremental() %}
    WHERE day > (SELECT MAX(day) FROM {{ this }})
{% endif %}