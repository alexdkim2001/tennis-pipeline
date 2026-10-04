"""ATP player-analysis dashboard.

Reads from the gold layer (workspace.tennis_gold) built by tennis_dbt.
Nothing here computes stats - every number is already aggregated by dbt;
this page just queries, caches, and charts it.

Run: streamlit run dashboard/app.py
"""
import pandas as pd
import streamlit as st

import charts
import db

st.set_page_config(page_title="ATP Player Dashboard", layout="wide")

st.title("ATP Player Dashboard")
st.caption("Source: TML-Database (2015-2025) -> Databricks bronze -> silver -> gold via dbt.")

overview = db.load_player_overview()

if overview.empty:
    st.warning("gold_player_overview is empty - run `cd tennis_dbt && dbt build` first.")
    st.stop()

player_names = sorted(overview["player_name"].dropna().unique())
selected_name = st.sidebar.selectbox("Player", player_names)
player_row = overview.loc[overview["player_name"] == selected_name].iloc[0]
player_id = int(player_row["player_id"])

st.sidebar.caption(
    f"Ranking as of {player_row['rank_as_of']:%b %Y}"
    if pd.notna(player_row["rank_as_of"]) else "No ranking on record"
)
st.sidebar.divider()
st.sidebar.caption("Data refreshes automatically within 5 minutes of the next `dbt build`.")

# --- KPI row -----------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Matches played", f"{int(player_row['matches_played']):,}")
col2.metric("Win-loss", f"{int(player_row['wins'])}-{int(player_row['losses'])}")
col3.metric("Win %", f"{player_row['win_pct']:.0%}")
rank_display = f"#{int(player_row['current_rank'])}" if pd.notna(player_row["current_rank"]) else "Unranked"
col4.metric("Current rank", rank_display)

st.divider()

# --- Surface + ranking trend --------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Win % by surface")
    surface_df = db.load_surface_stats(player_id)
    if surface_df.empty:
        st.info("No surface data for this player.")
    else:
        st.plotly_chart(charts.surface_win_pct_bar(surface_df), use_container_width=True)

with right:
    st.subheader("Ranking over time")
    rank_df = db.load_ranking_history(player_id)
    if rank_df.empty:
        st.info("No ranking history for this player.")
    else:
        st.plotly_chart(charts.ranking_trend_line(rank_df), use_container_width=True)

st.divider()

# --- Head-to-head ---------------------------------------------------------
st.subheader("Head-to-head")
opponent_names = [n for n in player_names if n != selected_name]
selected_opponent = st.selectbox("Opponent", opponent_names)
opponent_id = int(overview.loc[overview["player_name"] == selected_opponent, "player_id"].iloc[0])

h2h_df = db.load_head_to_head(player_id, opponent_id)

if h2h_df.empty:
    st.info(f"{selected_name} and {selected_opponent} haven't played each other.")
else:
    row = h2h_df.iloc[0]
    st.plotly_chart(
        charts.head_to_head_bar(selected_name, selected_opponent, int(row["wins"]), int(row["losses"])),
        use_container_width=True,
    )
    st.caption(f"{int(row['matches_played'])} matches - last played {row['last_played']:%b %Y}")
