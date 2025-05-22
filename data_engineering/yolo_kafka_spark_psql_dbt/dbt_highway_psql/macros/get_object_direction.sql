{% macro get_object_direction(direction_angle_degrees_column) %}
    CASE
        WHEN {{ direction_angle_degrees_column }} IS NULL THEN 'Stop'
        WHEN {{ direction_angle_degrees_column }} >= 337.5 OR {{ direction_angle_degrees_column }} < 22.5  THEN 'E'
        WHEN {{ direction_angle_degrees_column }} >= 22.5  AND {{ direction_angle_degrees_column }} < 67.5  THEN 'SE'
        WHEN {{ direction_angle_degrees_column }} >= 67.5  AND {{ direction_angle_degrees_column }} < 112.5 THEN 'S'
        WHEN {{ direction_angle_degrees_column }} >= 112.5 AND {{ direction_angle_degrees_column }} < 157.5 THEN 'SW'
        WHEN {{ direction_angle_degrees_column }} >= 157.5 AND {{ direction_angle_degrees_column }} < 202.5 THEN 'W'
        WHEN {{ direction_angle_degrees_column }} >= 202.5 AND {{ direction_angle_degrees_column }} < 247.5 THEN 'NW'
        WHEN {{ direction_angle_degrees_column }} >= 247.5 AND {{ direction_angle_degrees_column }} < 292.5 THEN 'N'
        WHEN {{ direction_angle_degrees_column }} >= 292.5 AND {{ direction_angle_degrees_column }} < 337.5 THEN 'NE'
        ELSE 'unknow' 
    END
{% endmacro %}