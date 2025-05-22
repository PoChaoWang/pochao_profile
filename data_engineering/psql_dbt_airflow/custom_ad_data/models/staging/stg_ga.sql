WITH source AS (
    SELECT
        *
    FROM
        {{ source(
            'destination_db',
            'ga_data'
        ) }}
),
renamed AS (
    SELECT
        DAY,
        utm_source AS "source",
        utm_medium AS medium,
        utm_campaign AS campaign,
        utm_content AS adgroup,
        total_users,
        first_time_purchasers,
        new_users,
        bounce_rate,
        sessions,
        engaged_sessions,
        purchase_revenue,
        purchases
    FROM
        source
)
SELECT
    *
FROM
    renamed
