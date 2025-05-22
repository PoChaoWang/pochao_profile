{{
    config(
        materialized='incremental',
        unique_key='uuid'
    )
}}

SELECT
    *
FROM {{ ref('stg_highway_traffic_raw') }}