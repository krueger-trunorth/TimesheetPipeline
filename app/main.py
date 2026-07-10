'''
----------------------------------------------------------------------------------------------------------------------
                                                App
----------------------------------------------------------------------------------------------------------------------
This file contains the main app for the TruNorth Timesheet datatables ingest and dashboard.
Using Plotly Dash, we create a simple to understand dashboard that allows users to graphically view timesheet data.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries
import os

import dash
from dash import Input, Output, dcc, html
import dash_mantine_components as dmc

from app.pages.dashboard_page import DashboardPage
from app.pages.ingest_page import IngestPage
from app.ui.trunorth.footer import Footer, FooterLink
from app.ui.trunorth.navbar import Navbar, NavPage

# app definitions
_APP_DIR = os.path.dirname(os.path.abspath(__file__))

# dash-mantine-components requires React 18+ (useId); Dash 2.x defaults to React 16.
dash._dash_renderer._set_react_version("18.2.0")

app = dash.Dash(
    __name__,
    assets_folder=os.path.join(_APP_DIR, "img"),
    suppress_callback_exceptions=True,
)
server = app.server

# page definitions
NAV_PAGES = [
    NavPage(label="Dashboard", href="/"),
    NavPage(label="Ingest", href="/ingest"),
]

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

DASHBOARD_PAGE = DashboardPage()
DASHBOARD_PAGE.register_callbacks(app)

INGEST_PAGE = IngestPage()
INGEST_PAGE.register_callbacks(app)

# dashboard layout
app.layout = dmc.MantineProvider(
    html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.Div(id="navbar-container"),
            dmc.Container(
                html.Div(id="page-content"),
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


# page routing
@app.callback(
    Output("navbar-container", "children"),
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname: str | None):
    active_path = pathname or "/"

    navbar = Navbar(
        logo_src="/assets/trunorth-logo.png",
        pages=NAV_PAGES,
        active_path=active_path,
    ).layout()

    if active_path == "/ingest":
        return navbar, INGEST_PAGE.layout()

    return navbar, DASHBOARD_PAGE.layout()


# local entrypoint
if __name__ == "__main__":
    host = os.getenv("DASH_HOST", "0.0.0.0")
    port = int(os.getenv("DASH_PORT", "8050"))
    app.run(host=host, port=port, debug=True)
