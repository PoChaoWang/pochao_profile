{% macro n_weeks_ago(num_weeks) %}
    {{ dbt_utils.dateadd(datepart="week", interval=-1 * num_weeks, from_date_or_timestamp="CURRENT_DATE") }}
{% endmacro %}