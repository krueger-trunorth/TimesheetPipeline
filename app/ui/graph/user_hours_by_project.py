'''
----------------------------------------------------------------------------------------------------------------------
                                                User Hours By Project Graph
----------------------------------------------------------------------------------------------------------------------
Bar chart of total hours grouped by project for a selected employee.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries

import pandas as pd
import plotly.graph_objects as go

from app.ui.graph.chart_helpers import bar_figure


# graph definitions
GRAPH_ID = "user-hours-by-project-graph"


def build_user_hours_by_project_figure(df: pd.DataFrame, employee_name: str | None = None) -> go.Figure:
    """Build the user hours by project bar chart."""
    return bar_figure(
        df,
        title="Hours by Project",
        x_column="ProjectName",
        y_column="TotalHours",
        x_label="Project",
        color="#40c057",
    )
