'''
----------------------------------------------------------------------------------------------------------------------
                                                Weekly Hours By Employee Graph
----------------------------------------------------------------------------------------------------------------------
Bar chart of total hours grouped by week and employee.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries

import pandas as pd
import plotly.graph_objects as go

from app.ui.graph.chart_helpers import bar_figure, empty_figure


# graph definitions
GRAPH_ID = "weekly-hours-by-employee-graph"


def build_weekly_hours_by_employee_figure(df: pd.DataFrame) -> go.Figure:
    """Build the weekly hours by employee bar chart."""
    if df.empty:
        return empty_figure("Weekly Hours")

    plot_df = df.copy()
    plot_df["WeekLabel"] = pd.to_datetime(plot_df["WeekOf"]).dt.strftime("%Y-%m-%d")
    plot_df["SeriesLabel"] = plot_df["WeekLabel"] + " — " + plot_df["EmployeeName"]

    return bar_figure(
        plot_df,
        title="Weekly Hours",
        x_column="SeriesLabel",
        y_column="TotalHours",
        x_label="Week / Employee",
        color="#12b886",
    )
