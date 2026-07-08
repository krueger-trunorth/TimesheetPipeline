'''
----------------------------------------------------------------------------------------------------------------------
                                                Ingest Page   
----------------------------------------------------------------------------------------------------------------------
This page allows a user to upload a file or folder containing excel timesheets to be ingested into the database.
PDF not yet supported!
----------------------------------------------------------------------------------------------------------------------
'''

class IngestPage()
    def __init__(self, app):
        self.app = d.Dash(__name__)

    def callbacks(self):


    def layout(self):
        return html.Div([
            html.H1("Ingest Page"),
        ])