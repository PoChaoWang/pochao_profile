WITH source AS (
    SELECT
        *
    FROM
        {{ source(
            'destination_db',
            'google_data'
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
