'''
----------------------------------------------------------------------------------------------------------------------
                                                App   
----------------------------------------------------------------------------------------------------------------------
This file contains the main app for the TruNorth Timesheet datatables ingest and dashboard.
Using Plotly Dash, we create a simple to understand dashboard that allows users to graphically view timesheet data.

NOTE: V1 scaffold only. No page, database, or backend logic implemented yet. This just confirms the app runs locally.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries
import os

import dash
from dash import html
import dash_mantine_components as dmc

# app definitions
app = dash.Dash(__name__)
server = app.server

# page definitions

# dashboard layout
app.layout = dmc.MantineProvider(
    html.Div(
        [
            dmc.Title("TruNorth Timesheet Pipeline", order=1),
            dmc.Text("App is running. Pages not implemented yet."),
        ]
    )
)

# local entrypoint
if __name__ == "__main__":
    host = os.getenv("DASH_HOST", "0.0.0.0")
    port = int(os.getenv("DASH_PORT", "8050"))
    app.run(host=host, port=port, debug=True)
