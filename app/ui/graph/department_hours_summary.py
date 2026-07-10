'''
----------------------------------------------------------------------------------------------------------------------
                                                Department Hours Summary Graph
----------------------------------------------------------------------------------------------------------------------
Bar chart of total hours grouped by department.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries

import pandas as pd
import plotly.graph_objects as go

from app.ui.graph.chart_helpers import bar_figure


# graph definitions
GRAPH_ID = "department-hours-summary-graph"


def build_department_hours_summary_figure(df: pd.DataFrame) -> go.Figure:
    """Build the department hours summary bar chart."""
    return bar_figure(
        df,
        title="Department Hours",
        x_column="DepartmentName",
        y_column="TotalHours",
        x_label="Department",
        color="#fd7e14",
    )
