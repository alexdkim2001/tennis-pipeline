{# By default dbt prefixes a model's +schema config with the target schema
   (e.g. target_schema_tennis_silver). We want the schema used exactly as
   configured, so silver models land in workspace.tennis_silver and marts
   land in workspace.tennis_gold regardless of the target's default schema. #}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
