SELECT
    capture_date_utc AS date_utc,
    CAST(EXTRACT(YEAR FROM capture_date_utc) AS INTEGER) AS year,
    CAST(EXTRACT(MONTH FROM capture_date_utc) AS INTEGER) AS month,
    CAST(EXTRACT(DAY FROM capture_date_utc) AS INTEGER) AS day,
    capture_time_utc AS time_utc,
    CAST(SPLIT_PART(capture_time_utc, ':', 1) AS INTEGER) AS hour,
    CAST(SPLIT_PART(capture_time_utc, ':', 2) AS INTEGER) AS minute,
    CAST(SPLIT_PART(capture_time_utc, ':', 3) AS FLOAT) AS second,
    object_id,
    uuid,
    class,
    bounding_box_x1 AS bounding_box_left_top_x,
    bounding_box_y1 AS bounding_box_left_top_y,
    bounding_box_x2 AS bounding_box_right_bottom_x,
    bounding_box_y2 AS bounding_box_right_bottom_y,
    confidence,
    center_pixels_x,
    center_pixels_y,
    zone_name,
    speed_kmh
FROM {{ source('dbt_highway_sql', 'highway_traffic_raw')}}
{% if is_incremental() %}
WHERE capture_date_utc > (SELECT max(date_utc) FROM {{ this }})
{% endif %}