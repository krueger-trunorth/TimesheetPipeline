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

from app.ui.trunorth.footer import Footer, FooterLink
from app.ui.trunorth.navbar import Navbar, NavPage

# app definitions
_APP_DIR = os.path.dirname(os.path.abspath(__file__))

app = dash.Dash(
    __name__,
    assets_folder=os.path.join(_APP_DIR, "img"),
)
server = app.server

# page definitions
NAVBAR = Navbar(
    logo_src="/assets/trunorth-logo.png",
    pages=[
        NavPage(label="Dashboard", href="/"),
        NavPage(label="Ingest", href="/ingest"),
    ],
    active_path="/",
)

FOOTER = Footer(
    links=[
        FooterLink(label="TruNorth Operations Center", href="#"),
        FooterLink(label="TruNorth Website", href="#"),
        FooterLink(label="TruNorth SharePoint", href="#"),
    ],
    developer_docs=FooterLink(label="Developer Docs (Gollum)", href="#"),
    github_href="#",
    copyright_text="Copyright © TruNorth. All Rights Reserved.",
)

# dashboard layout
app.layout = dmc.MantineProvider(
    html.Div(
        [
            NAVBAR.layout(),
            dmc.Container(
                [
                    dmc.Title("TruNorth Timesheet Pipeline", order=1),
                    dmc.Text("App is running. Pages not implemented yet."),
                ],
                fluid=True,
                py="md",
                style={"flex": 1},
            ),
            FOOTER.layout(),
        ],
        style={
            "minHeight": "100vh",
            "display": "flex",
            "flexDirection": "column",
        },
    )
)

# local entrypoint
if __name__ == "__main__":
    host = os.getenv("DASH_HOST", "0.0.0.0")
    port = int(os.getenv("DASH_PORT", "8050"))
    app.run(host=host, port=port, debug=True)
