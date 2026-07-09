'''
----------------------------------------------------------------------------------------------------------------------
                                                Data Upsert Functions
----------------------------------------------------------------------------------------------------------------------
This file contains the data upsert functions for the TruNorth Timesheet datatables.
Using SQLAlchemy, we can upsert data into the database given a pandas dataframe (extracted within timesheet_parser.py)
----------------------------------------------------------------------------------------------------------------------
'''
from __future__ import annotations

# import libraries
from datetime import date, datetime
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.data_model import (
    Department,
    Employee,
    JobTitle,
    Project,
    SessionLocal,
    TaskCategory,
    Timecard,
    Timelog,
    init_db,
)

TimelogKey = tuple[int, str, date]


# session helpers
def create_session() -> Session:
    engine = init_db()
    return SessionLocal(bind=engine)()


# coercion helpers
def _coerce_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"Invalid date value: {value!r}")
    return parsed.date()


def _coerce_optional_str(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None


def _split_employee_name(name: str) -> tuple[str, str]:
    parts = name.strip().split()
    if not parts:
        raise ValueError("Employee name is empty.")
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _resolve_employee_names(row: pd.Series) -> tuple[str, str]:
    if "FirstName" in row and "LastName" in row:
        first_name = _coerce_optional_str(row["FirstName"])
        last_name = _coerce_optional_str(row["LastName"])
        if not first_name or last_name is None:
            raise ValueError("Employee row must include FirstName and LastName.")
        return first_name, last_name

    employee_name = _coerce_optional_str(row.get("EmployeeName"))
    if not employee_name:
        raise ValueError("Employee row must include EmployeeName or FirstName/LastName.")
    return _split_employee_name(employee_name)


# lookup helpers
def _find_department(session: Session, department_name: str) -> Department | None:
    return session.scalar(
        select(Department).where(Department.DepartmentName == department_name)
    )


def _find_job_title(session: Session, title_name: str) -> JobTitle | None:
    return session.scalar(select(JobTitle).where(JobTitle.TitleName == title_name))


def _find_employee(session: Session, first_name: str, last_name: str) -> Employee | None:
    return session.scalar(
        select(Employee).where(
            Employee.FirstName == first_name,
            Employee.LastName == last_name,
        )
    )


def _find_project(session: Session, project_name: str) -> Project | None:
    return session.scalar(select(Project).where(Project.ProjectName == project_name))


def _find_task_category(session: Session, task: str) -> TaskCategory | None:
    return session.scalar(select(TaskCategory).where(TaskCategory.Task == task))


def _find_timecard(session: Session, employee_id: int, week_of: date) -> Timecard | None:
    return session.scalar(
        select(Timecard).where(
            Timecard.EmployeeID == employee_id,
            Timecard.WeekOf == week_of,
        )
    )


def _find_timelog(
    session: Session,
    timecard_id: int,
    project_id: int,
    task: str,
    log_date: date,
) -> Timelog | None:
    return session.scalar(
        select(Timelog).where(
            Timelog.TimecardID == timecard_id,
            Timelog.ProjectID == project_id,
            Timelog.Task == task,
            Timelog.Date == log_date,
        )
    )


# table upserts
def upsert_departments(session: Session, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        department_name = _coerce_optional_str(row["DepartmentName"])
        if not department_name:
            continue

        department = _find_department(session, department_name)
        if department is None:
            session.add(Department(DepartmentName=department_name))


def upsert_job_titles(session: Session, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        title_name = _coerce_optional_str(row["TitleName"])
        if not title_name:
            continue

        job_title = _find_job_title(session, title_name)
        if job_title is None:
            session.add(JobTitle(TitleName=title_name))


def upsert_employees(session: Session, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        first_name, last_name = _resolve_employee_names(row)
        employee = _find_employee(session, first_name, last_name)

        job_title_name = _coerce_optional_str(row.get("TitleName") or row.get("JobTitle"))
        department_name = _coerce_optional_str(row.get("DepartmentName") or row.get("Department"))
        job_title_id = row.get("JobTitleID")
        department_id = row.get("DepartmentID")
        manager_id = row.get("ManagerID")

        if job_title_name:
            job_title = _find_job_title(session, job_title_name)
            if job_title is None:
                job_title = JobTitle(TitleName=job_title_name)
                session.add(job_title)
                session.flush()
            job_title_id = job_title.JobTitleID

        if department_name:
            department = _find_department(session, department_name)
            if department is None:
                department = Department(DepartmentName=department_name)
                session.add(department)
                session.flush()
            department_id = department.DepartmentID

        if employee is None:
            session.add(
                Employee(
                    FirstName=first_name,
                    LastName=last_name,
                    Email=_coerce_optional_str(row.get("Email")),
                    Phone=_coerce_optional_str(row.get("Phone")),
                    JobTitleID=int(job_title_id) if pd.notna(job_title_id) else None,
                    DepartmentID=int(department_id) if pd.notna(department_id) else None,
                    ManagerID=int(manager_id) if pd.notna(manager_id) else None,
                )
            )
            continue

        employee.Email = _coerce_optional_str(row.get("Email")) or employee.Email
        employee.Phone = _coerce_optional_str(row.get("Phone")) or employee.Phone
        if pd.notna(job_title_id):
            employee.JobTitleID = int(job_title_id)
        if pd.notna(department_id):
            employee.DepartmentID = int(department_id)
        if pd.notna(manager_id):
            employee.ManagerID = int(manager_id)


def upsert_projects(session: Session, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        project_name = _coerce_optional_str(row["ProjectName"])
        if not project_name:
            continue

        customer_id = row.get("CustomerID")
        project = _find_project(session, project_name)
        if project is None:
            session.add(
                Project(
                    ProjectName=project_name,
                    CustomerID=int(customer_id) if pd.notna(customer_id) else None,
                )
            )
            continue

        if pd.notna(customer_id):
            project.CustomerID = int(customer_id)


def upsert_task_categories(session: Session, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        task = _coerce_optional_str(row.get("Task") or row.get("TaskName"))
        if not task:
            continue

        if _find_task_category(session, task) is None:
            session.add(TaskCategory(Task=task))


def upsert_timecards(session: Session, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        week_of = _coerce_date(row["WeekOf"])
        status = _coerce_optional_str(row.get("Status"))

        employee_id = row.get("EmployeeID")
        if pd.isna(employee_id):
            first_name, last_name = _resolve_employee_names(row)
            employee = _find_employee(session, first_name, last_name)
            if employee is None:
                employee = Employee(FirstName=first_name, LastName=last_name)
                session.add(employee)
                session.flush()
            employee_id = employee.EmployeeID
        else:
            employee_id = int(employee_id)

        timecard = _find_timecard(session, employee_id, week_of)
        if timecard is None:
            session.add(
                Timecard(
                    EmployeeID=employee_id,
                    WeekOf=week_of,
                    Status=status,
                )
            )
            continue

        timecard.Status = status


def upsert_timelogs(session: Session, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        timecard_id = row.get("TimecardID")
        if pd.isna(timecard_id):
            raise ValueError("Timelog rows must include TimecardID.")
        timecard_id = int(timecard_id)

        project_name = _coerce_optional_str(row.get("Project") or row.get("ProjectName"))
        task = _coerce_optional_str(row.get("Task") or row.get("TaskName"))
        if not project_name or not task:
            continue

        project = _find_project(session, project_name)
        if project is None:
            project = Project(ProjectName=project_name)
            session.add(project)
            session.flush()

        if _find_task_category(session, task) is None:
            session.add(TaskCategory(Task=task))
            session.flush()

        log_date = _coerce_date(row["Date"])
        hours = float(row["Hours"])
        timelog = _find_timelog(session, timecard_id, project.ProjectID, task, log_date)
        if timelog is None:
            session.add(
                Timelog(
                    TimecardID=timecard_id,
                    ProjectID=project.ProjectID,
                    Task=task,
                    Date=log_date,
                    Hours=hours,
                )
            )
            continue

        timelog.Hours = hours


# parsed timesheet upsert
def upsert_timesheet_dataframes(
    timecard_df: pd.DataFrame,
    timelog_df: pd.DataFrame,
    session: Session | None = None,
) -> Timecard:
    owns_session = session is None
    if owns_session:
        session = create_session()

    try:
        if timecard_df.empty:
            raise ValueError("Timecard dataframe is empty.")

        timecard_row = timecard_df.iloc[0]
        first_name, last_name = _resolve_employee_names(timecard_row)
        employee = _find_employee(session, first_name, last_name)
        if employee is None:
            employee = Employee(FirstName=first_name, LastName=last_name)
            session.add(employee)
            session.flush()

        week_of = _coerce_date(timecard_row["WeekOf"])
        status = _coerce_optional_str(timecard_row.get("Status"))
        timecard = _find_timecard(session, employee.EmployeeID, week_of)
        if timecard is None:
            timecard = Timecard(
                EmployeeID=employee.EmployeeID,
                WeekOf=week_of,
                Status=status,
            )
            session.add(timecard)
            session.flush()
        else:
            timecard.Status = status

        incoming_keys: set[TimelogKey] = set()
        for _, row in timelog_df.iterrows():
            project_name = _coerce_optional_str(row.get("Project"))
            task = _coerce_optional_str(row.get("Task"))
            if not project_name or not task:
                continue

            project = _find_project(session, project_name)
            if project is None:
                project = Project(ProjectName=project_name)
                session.add(project)
                session.flush()

            if _find_task_category(session, task) is None:
                session.add(TaskCategory(Task=task))
                session.flush()

            log_date = _coerce_date(row["Date"])
            hours = float(row["Hours"])
            key = (project.ProjectID, task, log_date)
            incoming_keys.add(key)

            timelog = _find_timelog(
                session,
                timecard.TimecardID,
                project.ProjectID,
                task,
                log_date,
            )
            if timelog is None:
                session.add(
                    Timelog(
                        TimecardID=timecard.TimecardID,
                        ProjectID=project.ProjectID,
                        Task=task,
                        Date=log_date,
                        Hours=hours,
                    )
                )
            else:
                timelog.Hours = hours

        for timelog in session.scalars(
            select(Timelog).where(Timelog.TimecardID == timecard.TimecardID)
        ):
            key = (timelog.ProjectID, timelog.Task, timelog.Date)
            if key not in incoming_keys:
                session.delete(timelog)

        if owns_session:
            session.commit()

        return timecard
    except Exception:
        if owns_session:
            session.rollback()
        raise
    finally:
        if owns_session:
            session.close()
