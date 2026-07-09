# Excel Spreadsheet Parsing 
This is a reference specifying how the excel spreadsheet should be parsed.
TruNorth uses a custom timesheet template which has a structure which is easily parsable. Note that the horizontal size is always the same, starting at A1 and ending at I1, however the vertical sizing varies by the number of distinct project-task pairs.

## Example Timesheet
![Example Timesheet](timesehet.png)

Table Headers:
Project (A)
Task (B)
Monday (C6) / Monday Date (C7)
Tuesday (D6) / Tuesday Date (D7)
Wednesday (E6) / Wednesday Date (E7)
Thursday (F6) / Thursday Date (F7)
Friday (G6) / Friday Date (G7)
Saturday (H6) / Saturday Date (H7)
Sunday (I6) / Sunday Date (I7)

The totals sections are not relevant to how we are storing the information within the database, however these can be used as Horizontal and Vertical boundaries when parsing.

Horizontal Boundary (static): Column J
Vertical Boundary (dynamic): find "Totals" within Column B. 

## Project and Task
Each row within the timesheet card has hours mapped to a specific Projec and Task. This is a many to many relationship, but the important piece of this is that all hours logged per date on a row maps to the row's specific Project and Task config. 

Database tables should be populated in such a way that I can write a group by that seperates the project hours by task. 


## Parsing Directions
For each timecard, there will be one "Timecard" entry on the database:
- TimecardID: auto inc
- EmployeeID: FK from "Employee" table searching on the name held within cell C3
- WeekOf: convert the date held within C4 cell
- Status: leave null for now

For each row in the timecard (not including the headers, so only where there are unique project/tasks):
create a timelog for each date (cell C7):
- TimelogID: auto inc
- TimecardID: FK from "Timecard"
- ProjectID: use cell A6 to look up a ProjectID within "Project" table
- TaskID: use cell B6 to look up a TaskID within "TaskCategories" table
- Date: use the date found within cell C7
- Hours: use the quantity found within the current cell


## EXAMPLE PARSING -> TABLE FROM IMAGE
Showing the Timelogs for only row 1 999999 - TruNorth Misc. (project) and Admin - Training (task)

Boundaries:
x: Column J ("TOTALS")
y: Row 12 ("Totals")

Name: Matt Krueger
WeekOf: 7/6/2026

Tables:
Timecard:
- TimecardID: 1
- EmployeeID: 1
- WeekOf: 7/6/2026
- Status: null

Timelog (1):
- TimelogID: 1
- TimecardID: 1 (from TimecardID)
- ProjectID: 1 (from Projects)
- TaskID: 1 (from TaskCategories)
- Date: 7/6/2026
- Hours: 6

Timelog (2):
- TimelogID: 1
- TimecardID: 1 (from TimecardID)
- ProjectID: 1 (from Projects)
- TaskID: 1 (from TaskCategories)
- Date: 7/7/2026
- Hours: 4

Timelog (3):
- TimelogID: 1
- TimecardID: 1 (from TimecardID)
- ProjectID: 1 (from Projects)
- TaskID: 1 (from TaskCategories)
- Date: 7/8/2026
- Hours: 5

no other timelog as the cells contain null/0 hours