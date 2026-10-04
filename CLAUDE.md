# Tennis Pipeline

Portfolio project: ATP match data → Databricks → dbt → player-analysis dashboard.
The user is a data enablement analyst learning data engineering — explain the "why", not just the "what".

## Architecture
- Source: TML-Database CSVs (GitHub), 2015–2025, ATP only
- [ingestion/ingest_tml.py](ingestion/ingest_tml.py): PySpark job, downloads to a UC volume, rebuilds bronze
  (`workspace.tennis_bronze.atp_matches`, all strings + `_source_file`, `_ingested_at`)
- [tennis_dbt/](tennis_dbt/): dbt-databricks project.
  - staging (`workspace.tennis_silver`) — `stg_atp_matches`: typed, deduped, `match_id` assigned
  - intermediate (`workspace.tennis_silver`) — `int_player_matches`: one row per player per match
  - marts (`workspace.tennis_gold`) — `gold_player_overview`, `gold_player_surface_stats`,
    `gold_player_ranking_history`, `gold_head_to_head`
- [dashboard/](dashboard/): Streamlit app reading the gold tables directly via `databricks-sql-connector`.
  Run with `streamlit run dashboard/app.py`; see dashboard/README.md for credentials setup.
- Medallion layers: bronze (raw) → silver (typed, deduped) → gold (player metrics) → dashboard

## Known data issues
- 489 rows (Aug 2025+) have null `match_num` → `match_id = md5(tourney_id|round|winner_id|loser_id)`
- 10 duplicate matches in source → deduped in `stg_atp_matches` (expect 30,707 rows)
- 2015–2020 files use CRLF line endings
- ~1,361 matches have no stats (walkovers, Davis Cup)

## Commands
- dbt: `cd tennis_dbt && dbt build`
- dashboard: `streamlit run dashboard/app.py` (needs `dashboard/.streamlit/secrets.toml`, see dashboard/README.md)

## Conventions
- Never print or commit credentials. `profiles.yml` lives in `~/.dbt`, outside the repo.
