'''
----------------------------------------------------------------------------------------------------------------------
                                                Data Model
----------------------------------------------------------------------------------------------------------------------
This file contains the data model used for the TruNorth Timesheet datatables.
Using SQLAlchemy, we define the tables and relationships between them as objects.
----------------------------------------------------------------------------------------------------------------------
'''
from __future__ import annotations

# import libraries
import os
from datetime import date
from pathlib import Path
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.engine import Engine
from sqlalchemy.event import listens_for
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


# declarative base
class Base(DeclarativeBase):
    pass


# reference tables
class Department(Base):
    __tablename__ = "Departments"

    DepartmentID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    DepartmentName: Mapped[str] = mapped_column(sa.String, nullable=False, unique=True)

    employees: Mapped[list[Employee]] = relationship(back_populates="department")


class JobTitle(Base):
    __tablename__ = "JobTitles"

    JobTitleID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    TitleName: Mapped[str] = mapped_column(sa.String, nullable=False, unique=True)

    employees: Mapped[list[Employee]] = relationship(back_populates="job_title")


class Employee(Base):
    __tablename__ = "Employees"

    EmployeeID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    FirstName: Mapped[str] = mapped_column(sa.String, nullable=False)
    LastName: Mapped[str] = mapped_column(sa.String, nullable=False)
    Email: Mapped[Optional[str]] = mapped_column(sa.String)
    Phone: Mapped[Optional[str]] = mapped_column(sa.String)
    JobTitleID: Mapped[Optional[int]] = mapped_column(sa.ForeignKey("JobTitles.JobTitleID"))
    DepartmentID: Mapped[Optional[int]] = mapped_column(sa.ForeignKey("Departments.DepartmentID"))
    ManagerID: Mapped[Optional[int]] = mapped_column(sa.ForeignKey("Employees.EmployeeID"))

    job_title: Mapped[Optional[JobTitle]] = relationship(back_populates="employees")
    department: Mapped[Optional[Department]] = relationship(back_populates="employees")
    manager: Mapped[Optional[Employee]] = relationship(
        remote_side=[EmployeeID],
        back_populates="direct_reports",
    )
    direct_reports: Mapped[list[Employee]] = relationship(back_populates="manager")
    timecards: Mapped[list[Timecard]] = relationship(back_populates="employee")


class Project(Base):
    __tablename__ = "Projects"

    ProjectID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    CustomerID: Mapped[Optional[int]] = mapped_column(sa.Integer)
    ProjectName: Mapped[str] = mapped_column(sa.String, nullable=False, unique=True)

    timelogs: Mapped[list[Timelog]] = relationship(back_populates="project")


class TaskCategory(Base):
    __tablename__ = "TaskCategories"

    TaskID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Task: Mapped[str] = mapped_column(sa.String, nullable=False, unique=True)

    timelogs: Mapped[list[Timelog]] = relationship(
        back_populates="task_category",
        primaryjoin="Timelog.Task == TaskCategory.Task",
        foreign_keys="Timelog.Task",
    )


class Timecard(Base):
    __tablename__ = "Timecards"

    TimecardID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    EmployeeID: Mapped[int] = mapped_column(sa.ForeignKey("Employees.EmployeeID"), nullable=False)
    WeekOf: Mapped[date] = mapped_column(sa.Date, nullable=False)
    Status: Mapped[Optional[str]] = mapped_column(sa.String)

    employee: Mapped[Employee] = relationship(back_populates="timecards")
    timelogs: Mapped[list[Timelog]] = relationship(
        back_populates="timecard",
        cascade="all, delete-orphan",
    )


class Timelog(Base):
    __tablename__ = "Timelogs"

    TimelogID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    TimecardID: Mapped[int] = mapped_column(sa.ForeignKey("Timecards.TimecardID"), nullable=False)
    ProjectID: Mapped[int] = mapped_column(sa.ForeignKey("Projects.ProjectID"), nullable=False)
    Task: Mapped[str] = mapped_column(sa.ForeignKey("TaskCategories.Task"), nullable=False)
    Date: Mapped[date] = mapped_column("Date", sa.Date, nullable=False)
    Hours: Mapped[float] = mapped_column(sa.Float, nullable=False)

    timecard: Mapped[Timecard] = relationship(back_populates="timelogs")
    project: Mapped[Project] = relationship(back_populates="timelogs")
    task_category: Mapped[TaskCategory] = relationship(
        back_populates="timelogs",
        primaryjoin="Timelog.Task == TaskCategory.Task",
        foreign_keys=[Task],
    )


# database helpers
_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = str(_REPO_ROOT / "data" / "timesheet.sqlite")


def get_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    db_path = os.getenv("SQLITE_DB_PATH", DEFAULT_SQLITE_PATH)
    return sa.URL.create(drivername="sqlite", database=db_path).render_as_string(hide_password=False)


@listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return sa.create_engine(url, connect_args=connect_args)


def init_db(engine: Engine | None = None) -> Engine:
    db_engine = engine or get_engine()

    if db_engine.url.drivername == "sqlite":
        db_file = db_engine.url.database
        if db_file and db_file != ":memory:":
            Path(db_file).parent.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(db_engine)
    return db_engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False)
