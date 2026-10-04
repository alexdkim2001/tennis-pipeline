"""Plotly figure builders.

Styling follows the dataviz skill: categorical hues assigned in fixed order
(never cycled), status colors reserved for win/loss state, one axis per
chart, muted hairline gridlines, a legend only when color is the sole
identity channel for 2+ series, and sparing direct labels (endpoint/tip
only - never a number on every point).
"""
import pandas as pd
import plotly.graph_objects as go

import colors

_FONT = dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif", color=colors.INK_PRIMARY)


def _base_layout(**overrides) -> dict:
    layout = dict(
        paper_bgcolor=colors.CHART_SURFACE,
        plot_bgcolor=colors.CHART_SURFACE,
        font=_FONT,
        margin=dict(l=40, r=20, t=10, b=40),
        showlegend=False,
    )
    layout.update(overrides)
    return layout


def surface_win_pct_bar(df: pd.DataFrame) -> go.Figure:
    """One bar per surface. x-axis labels already carry identity, so no
    legend box is needed even though color varies per bar."""
    df = df.sort_values("matches_played", ascending=False)
    bar_colors = [colors.SURFACE_COLOR.get(s, colors.INK_MUTED) for s in df["surface"]]

    fig = go.Figure(
        go.Bar(
            x=df["surface"],
            y=df["win_pct"] * 100,
            marker_color=bar_colors,
            text=[f"{v:.0%}" for v in df["win_pct"]],
            textposition="outside",
            textfont=dict(color=colors.INK_SECONDARY),
            customdata=df[["wins", "losses"]],
            hovertemplate="%{x}: %{customdata[0]}-%{customdata[1]} (%{y:.0f}%)<extra></extra>",
        )
    )
    fig.update_layout(**_base_layout(bargap=0.35))
    fig.update_yaxes(
        title=None, range=[0, 100], ticksuffix="%",
        gridcolor=colors.GRIDLINE, griddash="solid", zeroline=False,
        tickfont=dict(color=colors.INK_MUTED),
    )
    fig.update_xaxes(
        showgrid=False, linecolor=colors.BASELINE,
        tickfont=dict(color=colors.INK_SECONDARY),
    )
    return fig


def ranking_trend_line(df: pd.DataFrame) -> go.Figure:
    """Single series -> no legend (the subheader above already names it).
    Rank 1 is best, so the y-axis is reversed: the line visually climbs
    when the player is improving."""
    df = df.sort_values("tourney_date")

    fig = go.Figure(
        go.Scatter(
            x=df["tourney_date"],
            y=df["rank"],
            mode="lines+markers",
            line=dict(color=colors.SEQUENTIAL_BLUE, width=2),
            marker=dict(size=6, color=colors.SEQUENTIAL_BLUE,
                        line=dict(width=2, color=colors.CHART_SURFACE)),
            hovertemplate="%{x|%b %Y}: #%{y}<extra></extra>",
        )
    )
    fig.update_layout(**_base_layout())
    fig.update_yaxes(
        title=None, autorange="reversed",
        gridcolor=colors.GRIDLINE, zeroline=False,
        tickfont=dict(color=colors.INK_MUTED),
    )
    fig.update_xaxes(
        showgrid=False, linecolor=colors.BASELINE,
        tickfont=dict(color=colors.INK_SECONDARY),
    )
    return fig


def head_to_head_bar(player_name: str, opponent_name: str, wins: int, losses: int) -> go.Figure:
    """Wins/losses as state, not identity, so this uses the reserved status
    colors (good/critical) rather than a categorical hue. Category labels on
    the x-axis carry identity - no legend needed."""
    fig = go.Figure(
        go.Bar(
            x=["Wins", "Losses"],
            y=[wins, losses],
            marker_color=[colors.STATUS_GOOD, colors.STATUS_CRITICAL],
            text=[str(wins), str(losses)],
            textposition="outside",
            textfont=dict(color=colors.INK_SECONDARY),
            hovertemplate="%{x}: %{y}<extra></extra>",
        )
    )
    fig.update_layout(**_base_layout(bargap=0.5))
    fig.update_yaxes(
        title=None, gridcolor=colors.GRIDLINE, zeroline=False,
        tickfont=dict(color=colors.INK_MUTED), rangemode="tozero",
    )
    fig.update_xaxes(showgrid=False, linecolor=colors.BASELINE,
                      tickfont=dict(color=colors.INK_SECONDARY))
    return fig
