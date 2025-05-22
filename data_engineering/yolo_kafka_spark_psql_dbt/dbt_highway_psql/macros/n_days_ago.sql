{% macro n_days_ago(num_days) %}
    {{ dbt_utils.dateadd(datepart="day", interval=-1 * num_days, from_date_or_timestamp="CURRENT_DATE") }}
{% endmacro %}