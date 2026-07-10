''' 
----------------------------------------------------------------------------------------------------------------------
                                                Data Import Functions   
----------------------------------------------------------------------------------------------------------------------
This file contains the data import functions for the TruNorth Timesheet datatables.
Using SQLAlchemy, we can pull data from the database and return a pandas dataframe.
----------------------------------------------------------------------------------------------------------------------
'''
from __future__ import annotations

# import libraries
from datetime import date
from typing import Any

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.config import is_db_disabled
from app.db.data_model import Employee, Project, init_db


# engine helpers
_BASE_DETAIL_COLUMNS = [
    "TimelogID",
    "LogDate",
    "Hours",
    "Task",
    "ProjectID",
    "ProjectName",
    "TimecardID",
    "WeekOf",
    "TimecardStatus",
    "EmployeeID",
    "EmployeeName",
    "DepartmentName",
    "JobTitle",
]

_BASE_DETAIL_SQL = """
SELECT
    tl.TimelogID AS TimelogID,
    tl.Date AS LogDate,
    tl.Hours AS Hours,
    tl.Task AS Task,
    p.ProjectID AS ProjectID,
    p.ProjectName AS ProjectName,
    tc.TimecardID AS TimecardID,
    tc.WeekOf AS WeekOf,
    tc.Status AS TimecardStatus,
    e.EmployeeID AS EmployeeID,
    e.FirstName || ' ' || e.LastName AS EmployeeName,
    d.DepartmentName AS DepartmentName,
    jt.TitleName AS JobTitle
FROM Timelogs tl
JOIN Timecards tc ON tl.TimecardID = tc.TimecardID
JOIN Employees e ON tc.EmployeeID = e.EmployeeID
JOIN Projects p ON tl.ProjectID = p.ProjectID
LEFT JOIN Departments d ON e.DepartmentID = d.DepartmentID
LEFT JOIN JobTitles jt ON e.JobTitleID = jt.JobTitleID
"""


def _get_engine() -> Engine | None:
    if is_db_disabled():
        return None
    return init_db()


def _empty_df(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


# filter helpers
def _split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split()
    if not parts:
        raise ValueError("Employee name is empty.")
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _resolve_project(project: str | int, engine: Engine) -> tuple[str, int]:
    """Return (filter_column, value) for a project identifier."""
    if isinstance(project, int):
        return "ProjectID", project

    if not isinstance(project, str) or not project.strip():
        raise ValueError("Project identifier must be a non-empty string or int.")

    with engine.connect() as conn:
        project_id = conn.scalar(
            sa.select(Project.ProjectID).where(Project.ProjectName == project)
        )
    if project_id is None:
        raise ValueError(f"Project not found: {project}")
    return "ProjectID", project_id


def _resolve_employee(employee: str | int, engine: Engine) -> tuple[str, int]:
    """Return (filter_column, value) for an employee identifier."""
    if isinstance(employee, int):
        return "EmployeeID", employee

    if not isinstance(employee, str) or not employee.strip():
        raise ValueError("Employee identifier must be a non-empty string or int.")

    first_name, last_name = _split_name(employee)
    with engine.connect() as conn:
        employee_id = conn.scalar(
            sa.select(Employee.EmployeeID).where(
                Employee.FirstName == first_name,
                Employee.LastName == last_name,
            )
        )
    if employee_id is None:
        raise ValueError(f"Employee not found: {employee}")
    return "EmployeeID", employee_id


def _build_date_filters(
    start_date: date | None = None,
    end_date: date | None = None,
    week_of: date | None = None,
    *,
    log_date_column: str = "LogDate",
    week_of_column: str = "WeekOf",
) -> tuple[list[str], dict[str, Any]]:
    """Build parameterized WHERE clauses for date filters."""
    clauses: list[str] = []
    params: dict[str, Any] = {}

    if start_date is not None:
        clauses.append(f"{log_date_column} >= :start_date")
        params["start_date"] = start_date.isoformat()

    if end_date is not None:
        clauses.append(f"{log_date_column} <= :end_date")
        params["end_date"] = end_date.isoformat()

    if week_of is not None:
        clauses.append(f"{week_of_column} = :week_of")
        params["week_of"] = week_of.isoformat()

    return clauses, params


def _assemble_query(
    select_columns: list[str],
    group_by_columns: list[str] | None = None,
    aggregations: list[str] | None = None,
    filters: list[str] | None = None,
    order_by: list[str] | None = None,
) -> str:
    """Compose a query around the denormalized timelog base SQL."""
    select_parts = list(select_columns)
    if aggregations:
        select_parts.extend(aggregations)

    sql = f"SELECT {', '.join(select_parts)}\nFROM ({_BASE_DETAIL_SQL}) AS detail\n"

    if filters:
        sql += "WHERE " + " AND ".join(filters) + "\n"

    if group_by_columns:
        sql += "GROUP BY " + ", ".join(group_by_columns) + "\n"

    if order_by:
        sql += "ORDER BY " + ", ".join(order_by) + "\n"

    return sql


# public query functions
def get_project_hours_by_task(
    project: str | int,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    week_of: date | None = None,
) -> pd.DataFrame:
    """Return total hours per task for a specific project."""
    engine = _get_engine()
    if engine is None:
        return _empty_df(["ProjectName", "Task", "TotalHours"])

    column, value = _resolve_project(project, engine)
    date_clauses, params = _build_date_filters(start_date, end_date, week_of)
    filters = [f"{column} = :project_id"] + date_clauses
    params["project_id"] = value

    sql = _assemble_query(
        select_columns=["ProjectName", "Task"],
        aggregations=["SUM(Hours) AS TotalHours"],
        group_by_columns=["ProjectName", "Task"],
        filters=filters,
        order_by=["TotalHours DESC"],
    )

    return pd.read_sql(text(sql), engine, params=params)


def get_user_hours_by_project(
    employee: str | int,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    week_of: date | None = None,
) -> pd.DataFrame:
    """Return total hours per project for a specific user."""
    engine = _get_engine()
    if engine is None:
        return _empty_df(["EmployeeName", "ProjectName", "TotalHours"])

    column, value = _resolve_employee(employee, engine)
    date_clauses, params = _build_date_filters(start_date, end_date, week_of)
    filters = [f"{column} = :employee_id"] + date_clauses
    params["employee_id"] = value

    sql = _assemble_query(
        select_columns=["EmployeeName", "ProjectName"],
        aggregations=["SUM(Hours) AS TotalHours"],
        group_by_columns=["EmployeeName", "ProjectName"],
        filters=filters,
        order_by=["TotalHours DESC"],
    )

    return pd.read_sql(text(sql), engine, params=params)


def get_hours_by_date(
    *,
    project: str | int | None = None,
    employee: str | int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> pd.DataFrame:
    """Return daily total hours, optionally filtered by project and/or employee."""
    engine = _get_engine()
    if engine is None:
        return _empty_df(["LogDate", "ProjectName", "EmployeeName", "TotalHours"])

    date_clauses, params = _build_date_filters(start_date, end_date)
    group_by_columns = ["LogDate"]
    select_columns = ["LogDate"]

    if project is not None:
        column, value = _resolve_project(project, engine)
        select_columns.append("ProjectName")
        group_by_columns.extend(["ProjectID", "ProjectName"])
        date_clauses.append(f"{column} = :project_id")
        params["project_id"] = value
    else:
        select_columns.append("'All Projects' AS ProjectName")

    if employee is not None:
        column, value = _resolve_employee(employee, engine)
        select_columns.append("EmployeeName")
        group_by_columns.extend(["EmployeeID", "EmployeeName"])
        date_clauses.append(f"{column} = :employee_id")
        params["employee_id"] = value
    else:
        select_columns.append("'All Employees' AS EmployeeName")

    sql = _assemble_query(
        select_columns=select_columns,
        aggregations=["SUM(Hours) AS TotalHours"],
        group_by_columns=group_by_columns,
        filters=date_clauses or None,
        order_by=["LogDate"],
    )

    return pd.read_sql(text(sql), engine, params=params)


def get_weekly_hours_by_employee(
    *,
    employee: str | int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> pd.DataFrame:
    """Return total hours per week per employee."""
    engine = _get_engine()
    if engine is None:
        return _empty_df(["WeekOf", "EmployeeName", "TotalHours"])

    date_clauses, params = _build_date_filters(start_date, end_date)
    group_by_columns = ["WeekOf", "EmployeeID", "EmployeeName"]
    select_columns = ["WeekOf", "EmployeeName"]
    filters = list(date_clauses)

    if employee is not None:
        column, value = _resolve_employee(employee, engine)
        filters.append(f"{column} = :employee_id")
        params["employee_id"] = value

    sql = _assemble_query(
        select_columns=select_columns,
        aggregations=["SUM(Hours) AS TotalHours"],
        group_by_columns=group_by_columns,
        filters=filters or None,
        order_by=["WeekOf", "EmployeeName"],
    )

    return pd.read_sql(text(sql), engine, params=params)


def get_department_hours_summary(
    *,
    start_date: date | None = None,
    end_date: date | None = None,
) -> pd.DataFrame:
    """Return total hours grouped by department."""
    engine = _get_engine()
    if engine is None:
        return _empty_df(["DepartmentName", "TotalHours"])

    date_clauses, params = _build_date_filters(start_date, end_date)

    sql = _assemble_query(
        select_columns=["DepartmentName"],
        aggregations=["SUM(Hours) AS TotalHours"],
        group_by_columns=["DepartmentName"],
        filters=date_clauses or None,
        order_by=["TotalHours DESC"],
    )

    return pd.read_sql(text(sql), engine, params=params)


def get_task_hours_summary(
    *,
    start_date: date | None = None,
    end_date: date | None = None,
) -> pd.DataFrame:
    """Return total hours grouped by task across all projects."""
    engine = _get_engine()
    if engine is None:
        return _empty_df(["Task", "TotalHours"])

    date_clauses, params = _build_date_filters(start_date, end_date)

    sql = _assemble_query(
        select_columns=["Task"],
        aggregations=["SUM(Hours) AS TotalHours"],
        group_by_columns=["Task"],
        filters=date_clauses or None,
        order_by=["TotalHours DESC"],
    )

    return pd.read_sql(text(sql), engine, params=params)


def get_timelogs_detail(
    *,
    project: str | int | None = None,
    employee: str | int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    week_of: date | None = None,
) -> pd.DataFrame:
    """Return the full denormalized timelog detail table."""
    engine = _get_engine()
    if engine is None:
        return _empty_df(_BASE_DETAIL_COLUMNS)

    date_clauses, params = _build_date_filters(
        start_date,
        end_date,
        week_of,
        log_date_column="tl.Date",
        week_of_column="tc.WeekOf",
    )
    filters = list(date_clauses)

    if project is not None:
        column, value = _resolve_project(project, engine)
        filters.append(f"p.{column} = :project_id")
        params["project_id"] = value

    if employee is not None:
        column, value = _resolve_employee(employee, engine)
        filters.append(f"e.{column} = :employee_id")
        params["employee_id"] = value

    sql = _BASE_DETAIL_SQL
    if filters:
        sql += "WHERE " + " AND ".join(filters) + "\n"
    sql += "ORDER BY tl.Date, e.LastName, e.FirstName\n"

    return pd.read_sql(text(sql), engine, params=params)


# lookup helpers
def list_projects() -> pd.DataFrame:
    """Return all projects for dropdown selection."""
    engine = _get_engine()
    if engine is None:
        return _empty_df(["ProjectID", "ProjectName"])

    query = sa.select(Project.ProjectID, Project.ProjectName).order_by(Project.ProjectName)
    return pd.read_sql(query, engine)


def list_employees() -> pd.DataFrame:
    """Return all employees for dropdown selection."""
    engine = _get_engine()
    if engine is None:
        return _empty_df(["EmployeeID", "EmployeeName"])

    query = sa.select(
        Employee.EmployeeID,
        (Employee.FirstName + " " + Employee.LastName).label("EmployeeName"),
    ).order_by(Employee.LastName, Employee.FirstName)
    return pd.read_sql(query, engine)
