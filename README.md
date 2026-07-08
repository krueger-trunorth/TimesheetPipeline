# Timesheet Pipeline

This project is a work in progress pipeline for TruNorth timesheet data.

The goal is to ingest historical and future timesheets, store the parsed time logs in a relational database, and provide simple dashboards for visualizing hours spent on projects and their related project tasks.

As this is V1, both the database and dashboard are locally run within a docker container.

## Process
Ingest the timesheet information within the TruNorth Excel Timesheets (we use a template which makes this pretty easy), upsert (update or insert) this data into respective database tables, view data within dashboard.

## Database
The current database model is shown below. The green tables are the tables currently being operated on by this project. This is a rough draft of the TruNorth Database.
![Database diagram](database.png)

## Running the Application
Requires Docker + Docker Compose.

```bash
docker compose up --build
```

Then open the dashboard at [http://localhost:8050](http://localhost:8050).

To stop:

```bash
docker compose down
```
