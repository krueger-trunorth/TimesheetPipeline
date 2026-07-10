'''
----------------------------------------------------------------------------------------------------------------------
                                                Hours By Date Graph
----------------------------------------------------------------------------------------------------------------------
Line chart of daily total hours over time.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries

import pandas as pd
import plotly.graph_objects as go

from app.ui.graph.chart_helpers import line_figure


# graph definitions
GRAPH_ID = "hours-by-date-graph"


def build_hours_by_date_figure(df: pd.DataFrame) -> go.Figure:
    """Build the daily hours line chart."""
    return line_figure(
        df,
        title="Hours by Date",
        x_column="LogDate",
        y_column="TotalHours",
        x_label="Date",
        color="#7950f2",
    )
