{% macro yesterday() %}
    {{ dbt_utils.dateadd(datepart="day", interval=-1, from_date_or_timestamp="CURRENT_DATE") }}
{% endmacro %}