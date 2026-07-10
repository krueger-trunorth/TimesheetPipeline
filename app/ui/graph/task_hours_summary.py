'''
----------------------------------------------------------------------------------------------------------------------
                                                Task Hours Summary Graph
----------------------------------------------------------------------------------------------------------------------
Bar chart of total hours grouped by task across all projects.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries

import pandas as pd
import plotly.graph_objects as go

from app.ui.graph.chart_helpers import bar_figure


# graph definitions
GRAPH_ID = "task-hours-summary-graph"


def build_task_hours_summary_figure(df: pd.DataFrame) -> go.Figure:
    """Build the cross-project task hours summary bar chart."""
    return bar_figure(
        df,
        title="Hours by Task",
        x_column="Task",
        y_column="TotalHours",
        x_label="Task",
        color="#be4bdb",
    )
