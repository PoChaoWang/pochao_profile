WITH source AS (
    SELECT
        *
    FROM
        {{ source(
            'destination_db',
            'facebook_data'
        ) }}
),
renamed AS (
    SELECT
        *
    FROM
        source
)
SELECT
    *
FROM
    renamed
