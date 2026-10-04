# Dashboard

Streamlit app reading the gold layer (`workspace.tennis_gold`) built by
[tennis_dbt](../tennis_dbt). It's "live" in the sense that it queries
Databricks directly (not a static export) - results are cached 5 minutes
per query, so it reflects each `dbt build` within that window without
hitting the SQL warehouse on every click.

## What it shows

- **KPI tiles** - matches played, win-loss, win %, current rank
- **Win % by surface** - bar chart, one bar per surface
- **Ranking over time** - line chart, rank on an inverted axis (so "up" = improving)
- **Head-to-head** - pick a second player, see the pairwise record

Pick a player from the sidebar; everything else updates from there.

## Setup

1. Install dependencies (ideally in a virtualenv):
   ```
   pip install -r dashboard/requirements.txt
   ```
2. You need a running Databricks SQL warehouse and a personal access token.
3. Copy the secrets template and fill in your values:
   ```
   cp dashboard/.streamlit/secrets.toml.example dashboard/.streamlit/secrets.toml
   ```
   (`secrets.toml` is gitignored - never commit it.) Environment variables
   `DATABRICKS_HOST` / `DATABRICKS_HTTP_PATH` / `DATABRICKS_TOKEN` work too,
   as a fallback for deploying somewhere secrets.toml isn't convenient.
4. Make sure gold tables exist: `cd tennis_dbt && dbt build`.

## Run

```
streamlit run dashboard/app.py
```

## Deploying

For a shareable link, Streamlit Community Cloud works well: point it at
this repo, set `dashboard/app.py` as the entry point, and add the same
three values under the app's "Secrets" settings in place of a local
`secrets.toml`.
