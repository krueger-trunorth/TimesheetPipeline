'''
----------------------------------------------------------------------------------------------------------------------
                                                Chart Helpers
----------------------------------------------------------------------------------------------------------------------
Shared Plotly helpers for TruNorth dashboard graph components.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries

import pandas as pd
import plotly.graph_objects as go


# chart helpers
CHART_HEIGHT = 360


def empty_figure(title: str, message: str = "No data") -> go.Figure:
    """Return a placeholder figure when query results are empty."""
    figure = go.Figure()
    figure.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 14, "color": "#868e96"},
    )
    figure.update_layout(
        title=title,
        template="plotly_white",
        margin={"l": 40, "r": 20, "t": 50, "b": 40},
        height=CHART_HEIGHT,
        autosize=False,
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
    return figure


def bar_figure(
    df: pd.DataFrame,
    *,
    title: str,
    x_column: str,
    y_column: str,
    x_label: str,
    y_label: str = "Hours",
    color: str = "#228be6",
) -> go.Figure:
    """Build a horizontal-friendly vertical bar chart from a dataframe."""
    if df.empty:
        return empty_figure(title)

    figure = go.Figure(
        data=[
            go.Bar(
                x=df[x_column],
                y=df[y_column],
                marker_color=color,
                text=df[y_column].round(1),
                textposition="outside",
            )
        ]
    )
    figure.update_layout(
        title=title,
        template="plotly_white",
        xaxis_title=x_label,
        yaxis_title=y_label,
        margin={"l": 40, "r": 20, "t": 50, "b": 80},
        height=CHART_HEIGHT,
        autosize=False,
    )
    return figure


def line_figure(
    df: pd.DataFrame,
    *,
    title: str,
    x_column: str,
    y_column: str,
    x_label: str,
    y_label: str = "Hours",
    color: str = "#228be6",
) -> go.Figure:
    """Build a line chart from a dataframe."""
    if df.empty:
        return empty_figure(title)

    figure = go.Figure(
        data=[
            go.Scatter(
                x=df[x_column],
                y=df[y_column],
                mode="lines+markers",
                line={"color": color, "width": 2},
                marker={"size": 7},
            )
        ]
    )
    figure.update_layout(
        title=title,
        template="plotly_white",
        xaxis_title=x_label,
        yaxis_title=y_label,
        margin={"l": 40, "r": 20, "t": 50, "b": 60},
        height=CHART_HEIGHT,
        autosize=False,
    )
    return figure
