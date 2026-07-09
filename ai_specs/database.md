# Database (local dev)
The local development of this application will use a SQLite database, managed by the SQLAlchemy Python library.

# Database Tables
The following tables will be upserted (updated + inserted):
- Timecards (schema: timecards.png)
- Timelogs (schema: time_logs.png)
- Projects (schema: projects.png)
- TaskCategories (schema: task_categories.png)
- Employees (schema: employees.png)
- JobTitles (schema: job_titles.png)
- Departments (schema: departments.png)

Please ensure that these tables are first created if they do not persist. Additionally, these should persist within the volume of the SQLite Docker Image.

# Schema Definitions
Format: `Member (datatype) (relation)`. PK = primary key, FK = foreign key.

## Timecards
- TimecardID (int) (PK)
- EmployeeID (int) (FK)
- WeekOf (date)
- Status (str)

Relations:
- Timecards.TimecardID (1) -> Timelogs.TimecardID (1)

## Timelogs
- TimelogID (int) (PK)
- TimecardID (int) (FK -> Timecards.TimecardID)
- ProjectID (int) (FK -> Projects.ProjectID)
- Task (str) (FK -> TaskCategories.Task)
- Date (date)
- Hours (float)

Relations:
- Timelogs.TimecardID (1) -> Timecards.TimecardID (1)
- Timelogs.ProjectID (1) -> Projects.ProjectID (1)
- Timelogs.Task (1) -> TaskCategories.Task (1)

## Projects
- ProjectID (int) (PK)
- CustomerID (int) (FK)
- ProjectName (str)

Relations:
- Projects.ProjectID (1) -> Timelogs.ProjectID (1)

## TaskCategories
- TaskID (int) (PK)
- Task (str)

Relations:
- TaskCategories.Task (1) -> Timelogs.Task (1)

## Employees
- EmployeeID (int) (PK)
- FirstName (str)
- LastName (str)
- Email (str)
- Phone (str)
- JobTitleID (int) (FK -> JobTitles.JobTitleID)
- DepartmentID (int) (FK -> Departments.DepartmentID)
- ManagerID (int) (FK -> Employees.EmployeeID)

Relations:
- Employees.JobTitleID (1) -> JobTitles.JobTitleID (1)
- Employees.DepartmentID (1) -> Departments.DepartmentID (1)
- Employees.ManagerID (1) -> Employees.EmployeeID (1)

## JobTitles
- JobTitleID (int) (PK)
- TitleName (str)

Relations:
- JobTitles.JobTitleID (1) -> Employees.JobTitleID (1)

## Departments
- DepartmentID (int) (PK)
- DepartmentName (str)

Relations:
- Departments.DepartmentID (1) -> Employees.DepartmentID (1)
