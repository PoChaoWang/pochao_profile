{% macro n_months_ago(num_months) %}
    {{ dbt_utils.dateadd(datepart="month", interval=-1 * num_months, from_date_or_timestamp="CURRENT_DATE") }}
{% endmacro %}