"""Databricks SQL connection + cached queries against the gold layer.

Credentials come from Streamlit secrets (.streamlit/secrets.toml, gitignored)
or environment variables as a fallback - never hardcoded here. See README.md
for setup.

Every query result is cached for 5 minutes (st.cache_data ttl=300). That's
what makes this a "live" dashboard without hammering the SQL warehouse on
every click: it reflects the latest `dbt build` within 5 minutes, and
Streamlit's cache means most interactions (switching players, etc.) don't
re-query at all.
"""
import os

import pandas as pd
import streamlit as st
from databricks import sql

CATALOG = "workspace"
SCHEMA = "tennis_gold"


def _secret(key: str) -> str:
    if key in st.secrets:
        return st.secrets[key]
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            f"Missing {key}. Set it in .streamlit/secrets.toml or as an "
            "environment variable - see dashboard/README.md."
        )
    return value


def _connect():
    return sql.connect(
        server_hostname=_secret("DATABRICKS_HOST"),
        http_path=_secret("DATABRICKS_HTTP_PATH"),
        access_token=_secret("DATABRICKS_TOKEN"),
    )


def _query(sql_text: str) -> pd.DataFrame:
    with _connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql_text)
            return cursor.fetchall_arrow().to_pandas()


@st.cache_data(ttl=300, show_spinner="Loading players...")
def load_player_overview() -> pd.DataFrame:
    return _query(f"""
        select
            player_id, player_name, player_hand, player_ioc,
            matches_played, wins, losses, win_pct,
            current_rank, current_rank_points, rank_as_of
        from {CATALOG}.{SCHEMA}.gold_player_overview
        order by matches_played desc
    """)


@st.cache_data(ttl=300, show_spinner="Loading surface stats...")
def load_surface_stats(player_id: int) -> pd.DataFrame:
    player_id = int(player_id)  # guards against sql injection via interpolation below
    return _query(f"""
        select surface, matches_played, wins, losses, win_pct
        from {CATALOG}.{SCHEMA}.gold_player_surface_stats
        where player_id = {player_id}
        order by matches_played desc
    """)


@st.cache_data(ttl=300, show_spinner="Loading ranking history...")
def load_ranking_history(player_id: int) -> pd.DataFrame:
    player_id = int(player_id)
    return _query(f"""
        select tourney_date, rank, rank_points
        from {CATALOG}.{SCHEMA}.gold_player_ranking_history
        where player_id = {player_id}
        order by tourney_date
    """)


@st.cache_data(ttl=300, show_spinner="Loading head-to-head...")
def load_head_to_head(player_id: int, opponent_id: int) -> pd.DataFrame:
    player_id, opponent_id = int(player_id), int(opponent_id)
    return _query(f"""
        select matches_played, wins, losses, win_pct, last_played
        from {CATALOG}.{SCHEMA}.gold_head_to_head
        where player_id = {player_id} and opponent_id = {opponent_id}
    """)
