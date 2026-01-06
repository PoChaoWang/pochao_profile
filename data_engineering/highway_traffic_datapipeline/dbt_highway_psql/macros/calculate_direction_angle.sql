{% macro calculate_direction_angle(first_x, first_y, last_x, last_y) %}
    CASE
        WHEN {{ last_x }} = {{ first_x }} AND {{ last_y }} = {{ first_y }} THEN NULL
        ELSE
            MOD(
                CAST(
                    DEGREES(
                        ATAN2(
                            ({{ last_y }} - {{ first_y }}),
                            ({{ last_x }} - {{ first_x }})
                        )
                    ) + 360 AS NUMERIC),
                    360
            )
    END
{% endmacro %}