WITH all_platforms AS (
    SELECT
        *
    FROM
        {{ ref('stg_criteo') }}
    UNION ALL
    SELECT
        *
    FROM
        {{ ref('stg_facebook') }}
    UNION ALL
    SELECT
        *
    FROM
        {{ ref('stg_google') }}
    UNION ALL
    SELECT
        *
    FROM
        {{ ref('stg_yahoo') }}
),
ga AS (
    SELECT
        *
    FROM
        {{ ref('stg_ga') }}
),
join_all_data AS (
    SELECT
        p.day,
        p.campaign,
        p.adgroup,
        p.impressions,
        p.clicks,
        p.cost,
        g.total_users,
        g.first_time_purchasers,
        g.new_users,
        g.bounce_rate,
        g.sessions,
        g.engaged_sessions,
        g.purchase_revenue,
        g.purchases
    FROM
        all_platforms p
        LEFT JOIN ga g
        ON p.day = g.day
        AND p.campaign = g.campaign
        AND p.adgroup = g.adgroup
)
SELECT
    *
FROM
    join_all_data
