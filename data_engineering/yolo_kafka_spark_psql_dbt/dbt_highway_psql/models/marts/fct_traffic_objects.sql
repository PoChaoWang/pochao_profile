{{
    config(
        materialized='incremental',
        unique_key=['date_utc', 'object_id', 'class', 'zone_name'] 
    )
}}

WITH source_data AS (
    SELECT
        date_utc,
        time_utc,
        object_id,
        class,
        confidence,
        center_pixels_x,
        center_pixels_y,
        zone_name,
        speed_kmh
    FROM {{ ref('stg_highway_traffic_raw') }}
),

ranked_events AS (
    {{ add_bidirectional_rankings(
        relation='source_data',  
        partition_by_columns=['date_utc', 'object_id', 'class', 'zone_name'],
        order_by_column='time_utc'
    ) }}
),

aggregated_metrics AS (
    SELECT
        date_utc,
        object_id,
        class,
        zone_name,
        AVG(confidence) AS confidence,
        MAX(speed_kmh) AS speed_kmh
    FROM source_data
    GROUP BY
        date_utc,
        object_id,
        class,
        zone_name
),

first_point_data AS (
    SELECT
        date_utc,
        object_id,
        class,
        zone_name,
        time_utc AS earliest_time_utc,
        center_pixels_x AS first_center_x,
        center_pixels_y AS first_center_y
    FROM ranked_events
    WHERE rn_asc = 1
),

last_point_data AS (
    SELECT
        date_utc,
        object_id,
        class,
        zone_name,
        center_pixels_x AS last_center_x,
        center_pixels_y AS last_center_y
    FROM ranked_events
    WHERE rn_desc = 1
),

joined_data_with_points AS (
    SELECT
        agg.date_utc AS date_utc,
        fp.earliest_time_utc AS time_utc,
        agg.object_id AS object_id,
        agg.class AS class,
        agg.confidence AS confidence,
        fp.first_center_x AS first_center_x,
        fp.first_center_y AS first_center_y,
        lp.last_center_x AS last_center_x,
        lp.last_center_y AS last_center_y,
        agg.zone_name AS zone_name,
        agg.speed_kmh AS speed_kmh
    FROM aggregated_metrics agg
    JOIN first_point_data fp
        ON agg.date_utc = fp.date_utc
        AND agg.object_id = fp.object_id
        AND agg.class = fp.class
        AND agg.zone_name = fp.zone_name
    JOIN last_point_data lp
        ON agg.date_utc = lp.date_utc
        AND agg.object_id = lp.object_id
        AND agg.class = lp.class
        AND agg.zone_name = lp.zone_name
),

data_with_direction_angle AS (
    SELECT
        date_utc,
        time_utc,
        object_id,
        class,
        confidence,
        first_center_x,
        first_center_y,
        last_center_x,
        last_center_y,
        zone_name,
        speed_kmh,
        {{ calculate_direction_angle('first_center_x', 'first_center_y', 'last_center_x', 'last_center_y') }} AS direction_angle_degrees
    FROM joined_data_with_points
)

SELECT
    d.date_utc,
    d.time_utc,
    d.object_id,
    d.class,
    d.confidence,
    d.first_center_x,
    d.first_center_y,
    d.last_center_x,
    d.last_center_y,
    d.zone_name,
    d.speed_kmh,
    {{ get_object_direction('d.direction_angle_degrees') }} AS object_direction
FROM data_with_direction_angle d
ORDER BY
    d.date_utc,
    d.time_utc,
    d.object_id,
    d.class,
    d.zone_name