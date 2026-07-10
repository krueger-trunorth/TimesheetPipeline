'''
----------------------------------------------------------------------------------------------------------------------
                                                Ingest Page
----------------------------------------------------------------------------------------------------------------------
This page allows a user to upload a file or folder containing excel timesheets to be ingested into the database.
PDF not yet supported!
----------------------------------------------------------------------------------------------------------------------
'''
from __future__ import annotations

import base64
from io import BytesIO

import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, State, dcc, html, no_update

from app.config import is_db_disabled
from app.db.data_upsert import upsert_timesheet_dataframes
from app.utils.timesheet_parser import parse_timesheet_to_dataframes


class IngestPage:
    FILE_UPLOAD_ID = "ingest-file-upload"
    FOLDER_UPLOAD_ID = "ingest-folder-upload"
    STORE_ID = "ingest-parsed-store"
    STATUS_ID = "ingest-status"
    PREVIEW_ID = "ingest-preview"
    IMPORT_BTN_ID = "ingest-import-btn"

    EXCEL_SUFFIXES = (".xlsx", ".xls")

    def __init__(self, active_path: str = "/ingest") -> None:
        self.active_path = active_path

    def _status_alert(self, message: str, *, color: str = "blue") -> dmc.Alert:
        return dmc.Alert(message, color=color, variant="light")

    def _is_excel_file(self, filename: str) -> bool:
        return filename.lower().endswith(self.EXCEL_SUFFIXES)

    def _normalize_upload(
        self,
        contents: str | list[str] | None,
        filenames: str | list[str] | None,
    ) -> list[tuple[str, str]]:
        if not contents or not filenames:
            return []

        if isinstance(contents, str):
            return [(contents, filenames)]

        if isinstance(filenames, str):
            filenames = [filenames]

        return list(zip(contents, filenames))

    def _decode_upload(self, contents: str) -> BytesIO:
        if not contents or "," not in contents:
            raise ValueError("Upload payload is missing or invalid.")

        _, encoded = contents.split(",", 1)
        return BytesIO(base64.b64decode(encoded))

    def _parse_uploads(
        self,
        uploads: list[tuple[str, str]],
    ) -> tuple[list[dict], list[str]]:
        parsed_timesheets: list[dict] = []
        errors: list[str] = []

        for contents, filename in uploads:
            display_name = filename.split("/")[-1]
            if not self._is_excel_file(display_name):
                continue

            try:
                source = self._decode_upload(contents)
                timecard_df, timelog_df = parse_timesheet_to_dataframes(source)

                if timelog_df.empty:
                    raise ValueError("No billable hours found.")

                parsed_timesheets.append(
                    {
                        "filename": filename,
                        "timecard": timecard_df.to_dict(orient="records"),
                        "timelogs": timelog_df.to_dict(orient="records"),
                    }
                )
            except Exception as exc:
                errors.append(f"{display_name}: {exc}")

        return parsed_timesheets, errors

    def _preview_content(self, timesheets: list[dict]) -> list:
        if not timesheets:
            return []

        rows = []
        for timesheet in timesheets:
            timecard_df = pd.DataFrame(timesheet.get("timecard", []))
            timelog_df = pd.DataFrame(timesheet.get("timelogs", []))
            if timecard_df.empty:
                continue

            timecard_row = timecard_df.iloc[0]
            rows.append(
                html.Tr(
                    [
                        html.Td(timesheet["filename"].split("/")[-1]),
                        html.Td(str(timecard_row.get("EmployeeName", ""))),
                        html.Td(str(timecard_row.get("WeekOf", ""))),
                        html.Td(str(len(timelog_df))),
                        html.Td(f"{float(timelog_df['Hours'].sum()):.2f}" if not timelog_df.empty else "0.00"),
                    ]
                )
            )

        return [
            dmc.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("File"),
                                html.Th("Employee"),
                                html.Th("Week"),
                                html.Th("Rows"),
                                html.Th("Hours"),
                            ]
                        )
                    ),
                    html.Tbody(rows),
                ],
                withTableBorder=True,
                withColumnBorders=True,
            )
        ]

    def _upload_box(self, label: str, upload_id: str, *, multiple: bool) -> dcc.Upload:
        return dcc.Upload(
            id=upload_id,
            children=dmc.Box(
                dmc.Text(label, ta="center"),
                p="md",
                style={
                    "border": "1px dashed var(--mantine-color-gray-4)",
                    "borderRadius": "var(--mantine-radius-md)",
                    "cursor": "pointer",
                    "textAlign": "center",
                },
            ),
            multiple=multiple,
            accept=".xlsx,.xls",
            style={"width": "100%"},
        )

    def layout(self) -> html.Div:
        return html.Div(
            id="ingest-page",
            children=[
                dcc.Store(id=self.STORE_ID),
                dmc.SimpleGrid(
                    [
                        self._upload_box("Upload file", self.FILE_UPLOAD_ID, multiple=False),
                        self._upload_box("Upload folder", self.FOLDER_UPLOAD_ID, multiple=True),
                    ],
                    cols={"base": 1, "sm": 2},
                    spacing="md",
                ),
                html.Div(id=self.STATUS_ID, style={"marginTop": "1rem"}),
                html.Div(id=self.PREVIEW_ID, style={"marginTop": "1rem"}),
                dmc.Button(
                    "Import",
                    id=self.IMPORT_BTN_ID,
                    disabled=is_db_disabled(),
                    mt="md",
                ),
            ],
        )

    def register_callbacks(self, app) -> None:
        @app.callback(
            Output(self.STORE_ID, "data"),
            Output(self.STATUS_ID, "children"),
            Output(self.PREVIEW_ID, "children"),
            Output(self.IMPORT_BTN_ID, "disabled"),
            Input(self.FILE_UPLOAD_ID, "contents"),
            Input(self.FOLDER_UPLOAD_ID, "contents"),
            State(self.FILE_UPLOAD_ID, "filename"),
            State(self.FOLDER_UPLOAD_ID, "filename"),
            prevent_initial_call=True,
        )
        def handle_upload(
            file_contents: str | list[str] | None,
            folder_contents: str | list[str] | None,
            file_names: str | list[str] | None,
            folder_names: str | list[str] | None,
        ):
            uploads = self._normalize_upload(file_contents, file_names)
            uploads.extend(self._normalize_upload(folder_contents, folder_names))

            if not uploads:
                return no_update, no_update, no_update, is_db_disabled()

            try:
                timesheets, errors = self._parse_uploads(uploads)

                if not timesheets:
                    message = errors[0] if errors else "No Excel timesheets found."
                    return None, self._status_alert(message, color="red"), [], is_db_disabled()

                status_message = f"Parsed {len(timesheets)} timesheet(s)"
                if errors:
                    status_message += f", {len(errors)} failed"

                status = self._status_alert(status_message, color="green" if not errors else "yellow")
                if errors:
                    status = html.Div(
                        [
                            status,
                            dmc.Text("; ".join(errors), size="sm", c="dimmed", mt="xs"),
                        ]
                    )

                return (
                    {"timesheets": timesheets},
                    status,
                    self._preview_content(timesheets),
                    is_db_disabled(),
                )
            except Exception as exc:
                return None, self._status_alert(str(exc), color="red"), [], is_db_disabled()

        @app.callback(
            Output(self.STATUS_ID, "children", allow_duplicate=True),
            Output(self.STORE_ID, "data", allow_duplicate=True),
            Output(self.PREVIEW_ID, "children", allow_duplicate=True),
            Input(self.IMPORT_BTN_ID, "n_clicks"),
            State(self.STORE_ID, "data"),
            prevent_initial_call=True,
        )
        def handle_import(n_clicks: int | None, stored: dict | None):
            if not n_clicks:
                return no_update, no_update, no_update

            if is_db_disabled():
                return (
                    self._status_alert("Database disabled.", color="yellow"),
                    no_update,
                    no_update,
                )

            timesheets = (stored or {}).get("timesheets", [])
            if not timesheets:
                return (
                    self._status_alert("Upload timesheets first.", color="red"),
                    no_update,
                    no_update,
                )

            imported = 0
            errors: list[str] = []

            try:
                for timesheet in timesheets:
                    display_name = timesheet["filename"].split("/")[-1]
                    try:
                        timecard_df = pd.DataFrame(timesheet.get("timecard", []))
                        timelog_df = pd.DataFrame(timesheet.get("timelogs", []))
                        upsert_timesheet_dataframes(timecard_df, timelog_df)
                        imported += 1
                    except Exception as exc:
                        errors.append(f"{display_name}: {exc}")

                if imported == 0:
                    message = errors[0] if errors else "Import failed."
                    return self._status_alert(message, color="red"), no_update, no_update

                status_message = f"Imported {imported} timesheet(s)"
                status = self._status_alert(status_message, color="green" if not errors else "yellow")
                if errors:
                    status = html.Div(
                        [
                            status,
                            dmc.Text("; ".join(errors), size="sm", c="dimmed", mt="xs"),
                        ]
                    )

                return status, None, []
            except Exception as exc:
                return (
                    self._status_alert(str(exc), color="red"),
                    no_update,
                    no_update,
                )
