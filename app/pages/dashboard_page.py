'''
----------------------------------------------------------------------------------------------------------------------
                                                Dashboard Page   
----------------------------------------------------------------------------------------------------------------------
Page containing a bento grid of dashboards created using the timesheet data published to the database.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries

import pandas as pd
import dash_mantine_components as dmc
from dash import Input, Output, dcc, html

from app.db.data_import import (
    get_department_hours_summary,
    get_hours_by_date,
    get_project_hours_by_task,
    get_task_hours_summary,
    get_user_hours_by_project,
    get_weekly_hours_by_employee,
    list_employees,
    list_projects,
)
from app.ui.graph.chart_helpers import CHART_HEIGHT
from app.ui.graph.department_hours_summary import (
    GRAPH_ID as DEPARTMENT_GRAPH_ID,
    build_department_hours_summary_figure,
)
from app.ui.graph.hours_by_date import (
    GRAPH_ID as HOURS_BY_DATE_GRAPH_ID,
    build_hours_by_date_figure,
)
from app.ui.graph.project_hours_by_task import (
    GRAPH_ID as PROJECT_HOURS_GRAPH_ID,
    build_project_hours_by_task_figure,
)
from app.ui.graph.task_hours_summary import (
    GRAPH_ID as TASK_SUMMARY_GRAPH_ID,
    build_task_hours_summary_figure,
)
from app.ui.graph.user_hours_by_project import (
    GRAPH_ID as USER_HOURS_GRAPH_ID,
    build_user_hours_by_project_figure,
)
from app.ui.graph.weekly_hours_by_employee import (
    GRAPH_ID as WEEKLY_HOURS_GRAPH_ID,
    build_weekly_hours_by_employee_figure,
)


# dashboard page
class DashboardPage:
    PROJECT_DROPDOWN_ID = "dashboard-project-dropdown"
    EMPLOYEE_DROPDOWN_ID = "dashboard-employee-dropdown"

    def __init__(self, active_path: str = "/") -> None:
        self.active_path = active_path

    def _dropdown_options(self, labels: list[str]) -> list[dict[str, str]]:
        return [{"label": label, "value": label} for label in labels]

    def _project_options(self) -> tuple[list[dict[str, str]], str | None]:
        projects_df = list_projects()
        if projects_df.empty:
            return [], None
        labels = projects_df["ProjectName"].tolist()
        return self._dropdown_options(labels), labels[0]

    def _employee_options(self) -> tuple[list[dict[str, str]], str | None]:
        employees_df = list_employees()
        if employees_df.empty:
            return [], None
        labels = employees_df["EmployeeName"].tolist()
        return self._dropdown_options(labels), labels[0]

    def _empty_project_df(self) -> pd.DataFrame:
        return pd.DataFrame(columns=["ProjectName", "Task", "TotalHours"])

    def _empty_employee_df(self) -> pd.DataFrame:
        return pd.DataFrame(columns=["EmployeeName", "ProjectName", "TotalHours"])

    def _graph_card(self, graph_id: str, figure) -> dcc.Graph:
        return dcc.Graph(
            id=graph_id,
            figure=figure,
            config={"displayModeBar": False, "responsive": False},
            style={"height": f"{CHART_HEIGHT}px"},
        )

    def _filters_row(self) -> dmc.SimpleGrid:
        project_options, project_value = self._project_options()
        employee_options, employee_value = self._employee_options()

        return dmc.SimpleGrid(
            [
                dmc.Select(
                    id=self.PROJECT_DROPDOWN_ID,
                    label="Project",
                    data=project_options,
                    value=project_value,
                    searchable=True,
                    clearable=False,
                    disabled=not project_options,
                ),
                dmc.Select(
                    id=self.EMPLOYEE_DROPDOWN_ID,
                    label="Employee",
                    data=employee_options,
                    value=employee_value,
                    searchable=True,
                    clearable=False,
                    disabled=not employee_options,
                ),
            ],
            cols={"base": 1, "sm": 2},
            spacing="md",
            mb="md",
        )

    def layout(self) -> html.Div:
        _, project_value = self._project_options()
        _, employee_value = self._employee_options()

        project_df = (
            get_project_hours_by_task(project_value)
            if project_value
            else self._empty_project_df()
        )
        employee_df = (
            get_user_hours_by_project(employee_value)
            if employee_value
            else self._empty_employee_df()
        )

        return html.Div(
            id="dashboard-page",
            children=[
                self._filters_row(),
                dmc.SimpleGrid(
                    [
                        self._graph_card(
                            PROJECT_HOURS_GRAPH_ID,
                            build_project_hours_by_task_figure(project_df, project_value),
                        ),
                        self._graph_card(
                            USER_HOURS_GRAPH_ID,
                            build_user_hours_by_project_figure(employee_df, employee_value),
                        ),
                        self._graph_card(
                            HOURS_BY_DATE_GRAPH_ID,
                            build_hours_by_date_figure(get_hours_by_date()),
                        ),
                        self._graph_card(
                            DEPARTMENT_GRAPH_ID,
                            build_department_hours_summary_figure(get_department_hours_summary()),
                        ),
                        self._graph_card(
                            TASK_SUMMARY_GRAPH_ID,
                            build_task_hours_summary_figure(get_task_hours_summary()),
                        ),
                        self._graph_card(
                            WEEKLY_HOURS_GRAPH_ID,
                            build_weekly_hours_by_employee_figure(get_weekly_hours_by_employee()),
                        ),
                    ],
                    cols={"base": 1, "md": 2},
                    spacing="md",
                ),
            ],
        )

    def register_callbacks(self, app) -> None:
        @app.callback(
            Output(PROJECT_HOURS_GRAPH_ID, "figure"),
            Input(self.PROJECT_DROPDOWN_ID, "value"),
        )
        def update_project_hours_chart(project_name: str | None):
            if not project_name:
                return build_project_hours_by_task_figure(self._empty_project_df())
            return build_project_hours_by_task_figure(
                get_project_hours_by_task(project_name),
                project_name,
            )

        @app.callback(
            Output(USER_HOURS_GRAPH_ID, "figure"),
            Input(self.EMPLOYEE_DROPDOWN_ID, "value"),
        )
        def update_user_hours_chart(employee_name: str | None):
            if not employee_name:
                return build_user_hours_by_project_figure(self._empty_employee_df())
            return build_user_hours_by_project_figure(
                get_user_hours_by_project(employee_name),
                employee_name,
            )

        @app.callback(
            Output(HOURS_BY_DATE_GRAPH_ID, "figure"),
            Input(self.PROJECT_DROPDOWN_ID, "value"),
            Input(self.EMPLOYEE_DROPDOWN_ID, "value"),
        )
        def update_hours_by_date_chart(project_name: str | None, employee_name: str | None):
            return build_hours_by_date_figure(
                get_hours_by_date(
                    project=project_name,
                    employee=employee_name,
                )
            )
