{{ config(materialized='incremental') }}

SELECT
    *
FROM {{ ref('stg_highway_traffic_raw') }}