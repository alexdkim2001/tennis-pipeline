# tennis_dbt

dbt-databricks project. Builds silver (typed, deduped matches) and gold
(player-analysis) tables on top of `workspace.tennis_bronze.atp_matches`.

## Layers

- **staging** (`workspace.tennis_silver`) — `stg_atp_matches`: casts bronze's
  all-string columns to real types, assigns a stable `match_id`, dedupes.
- **intermediate** (`workspace.tennis_silver`) — `int_player_matches`:
  unpivots each match into one row per player (winner's row + loser's row).
  Not meant to be queried directly by the dashboard; everything downstream
  aggregates from this grain.
- **marts** (`workspace.tennis_gold`) — one table per dashboard need:
  - `gold_player_overview` — career record + current ranking per player
  - `gold_player_surface_stats` — win % by surface per player
  - `gold_player_ranking_history` — ranking over time per player
  - `gold_head_to_head` — pairwise record between any two players

## Setup

This project's profile is named `tennis_dbt`. Add it to `~/.dbt/profiles.yml`
(never commit this file):

```yaml
tennis_dbt:
  target: dev
  outputs:
    dev:
      type: databricks
      catalog: workspace
      schema: tennis_silver   # default; marts override to tennis_gold via +schema
      host: "{{ env_var('DATABRICKS_HOST') }}"
      http_path: "{{ env_var('DATABRICKS_HTTP_PATH') }}"
      token: "{{ env_var('DATABRICKS_TOKEN') }}"
      threads: 4
```

Set `DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, `DATABRICKS_TOKEN` in your
shell (or a local `.env` you source — never commit it).

## Run

```
cd tennis_dbt
dbt deps    # none currently required, but harmless if added later
dbt build   # runs models + schema tests
```
