'''
----------------------------------------------------------------------------------------------------------------------
                                                Project Hours By Task Graph
----------------------------------------------------------------------------------------------------------------------
Bar chart of total hours grouped by task for a selected project.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries

import pandas as pd
import plotly.graph_objects as go

from app.ui.graph.chart_helpers import bar_figure


# graph definitions
GRAPH_ID = "project-hours-by-task-graph"


def build_project_hours_by_task_figure(df: pd.DataFrame, project_name: str | None = None) -> go.Figure:
    """Build the project hours by task bar chart."""
    return bar_figure(
        df,
        title="Hours by Task",
        x_column="Task",
        y_column="TotalHours",
        x_label="Task",
        color="#228be6",
    )
