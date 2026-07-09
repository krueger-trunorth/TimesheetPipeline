'''
----------------------------------------------------------------------------------------------------------------------
                                                Timesheet Parser
----------------------------------------------------------------------------------------------------------------------
This file contains the timesheet parser functions for the TruNorth Timesheet datatables.
Using pandas, we can parse the excel file containing the timesheet data into a pandas dataframe.
----------------------------------------------------------------------------------------------------------------------
'''

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

import pandas as pd

# template layout (0-based indices)
EMPLOYEE_NAME_ROW = 2 #3
EMPLOYEE_NAME_COL = 2 #C
WEEK_OF_ROW = 3 #4
WEEK_OF_COL = 2 #C
DATE_ROW = 6 #7 
DATA_START_ROW = 7 #8
PROJECT_COL = 0 #A
TASK_COL = 1 #B
DAY_COL_START = 2 #C
DAY_COL_END = 8 #I
TOTALS_SEARCH_COL = 1 #B

TimesheetSource = Union[str, Path, BinaryIO, BytesIO]


@dataclass(frozen=True)
class ParsedTimecard:
    employee_name: str
    week_of: date
    status: None = None


@dataclass(frozen=True)
class ParsedTimelog:
    project: str
    task: str
    log_date: date
    hours: float


@dataclass(frozen=True)
class ParsedTimesheet:
    timecard: ParsedTimecard
    timelogs: tuple[ParsedTimelog, ...]

    def to_dataframes(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        timecard_df = pd.DataFrame(
            [
                {
                    "EmployeeName": self.timecard.employee_name,
                    "WeekOf": self.timecard.week_of,
                    "Status": self.timecard.status,
                }
            ]
        )
        timelog_df = pd.DataFrame(
            [
                {
                    "Project": timelog.project,
                    "Task": timelog.task,
                    "Date": timelog.log_date,
                    "Hours": timelog.hours,
                }
                for timelog in self.timelogs
            ]
        )
        return timecard_df, timelog_df


def parse_timesheet(source: TimesheetSource) -> ParsedTimesheet:
    sheet = _read_timesheet_sheet(source)
    employee_name = _extract_employee_name(sheet)
    week_of = _extract_week_of(sheet)
    day_dates = _extract_day_dates(sheet)
    totals_row = _find_totals_row(sheet)
    timelogs = _extract_timelogs(sheet, day_dates, totals_row)

    return ParsedTimesheet(
        timecard=ParsedTimecard(employee_name=employee_name, week_of=week_of),
        timelogs=tuple(timelogs),
    )


def parse_timesheet_to_dataframes(
    source: TimesheetSource,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    return parse_timesheet(source).to_dataframes()


def _read_timesheet_sheet(source: TimesheetSource) -> pd.DataFrame:
    return pd.read_excel(source, header=None, engine="openpyxl")


def _extract_employee_name(sheet: pd.DataFrame) -> str:
    value = sheet.iloc[EMPLOYEE_NAME_ROW, EMPLOYEE_NAME_COL]
    employee_name = _normalize_text(value)
    if not employee_name:
        raise ValueError("Employee name is missing from cell C3.")
    return employee_name


def _extract_week_of(sheet: pd.DataFrame) -> date:
    value = sheet.iloc[WEEK_OF_ROW, WEEK_OF_COL]
    week_of = _parse_date(value)
    if week_of is None:
        raise ValueError("Week starting date is missing or invalid in cell C4.")
    return week_of


def _extract_day_dates(sheet: pd.DataFrame) -> list[date]:
    day_dates: list[date] = []
    for col in range(DAY_COL_START, DAY_COL_END + 1):
        parsed_date = _parse_date(sheet.iloc[DATE_ROW, col])
        if parsed_date is None:
            raise ValueError(f"Missing or invalid date in row 7, column {col + 1}.")
        day_dates.append(parsed_date)
    return day_dates


def _find_totals_row(sheet: pd.DataFrame) -> int:
    for row in range(DATA_START_ROW, len(sheet)):
        cell_value = sheet.iloc[row, TOTALS_SEARCH_COL]
        if isinstance(cell_value, str) and cell_value.strip().lower() == "totals":
            return row
    raise ValueError('Could not find "Totals" row in column B.')


def _extract_timelogs(
    sheet: pd.DataFrame,
    day_dates: list[date],
    totals_row: int,
) -> list[ParsedTimelog]:
    timelogs: list[ParsedTimelog] = []

    for row in range(DATA_START_ROW, totals_row):
        project = _normalize_text(sheet.iloc[row, PROJECT_COL])
        task = _normalize_text(sheet.iloc[row, TASK_COL])
        if not project and not task:
            continue

        for day_index, log_date in enumerate(day_dates):
            col = DAY_COL_START + day_index
            hours = _parse_hours(sheet.iloc[row, col])
            if hours is None:
                continue

            timelogs.append(
                ParsedTimelog(
                    project=project,
                    task=task,
                    log_date=log_date,
                    hours=hours,
                )
            )

    return timelogs


def _normalize_text(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def _parse_date(value: object) -> date | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        parsed = pd.to_datetime(text, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date()
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _parse_hours(value: object) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        value = float(text)
    else:
        value = float(value)

    if value <= 0:
        return None
    return value
