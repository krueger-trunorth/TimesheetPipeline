'''
----------------------------------------------------------------------------------------------------------------------
                                                Dev Launcher
----------------------------------------------------------------------------------------------------------------------
This file runs the TruNorth Timesheet dashboard locally for fast UI development.
It bypasses Docker and the attached database, and enables Dash hot reload so UI edits refresh in the browser.
Intended for quick UI iteration only, not for full pipeline runs.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries
import os
import sys

# path setup so "app" package resolves when run from repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# dev entrypoint
def run_dev() -> None:
    # flag downstream code to skip the database (bypass docker container)
    os.environ.setdefault("DISABLE_DB", "1")

    # local host/port defaults
    host = os.getenv("DASH_HOST", "127.0.0.1")
    port = int(os.getenv("DASH_PORT", "8050"))

    # import app after env is set so it reads dev flags
    from app.main import app

    # run with hot reload enabled
    app.run(host=host, port=port, debug=True, use_reloader=True)


# local entrypoint
if __name__ == "__main__":
    run_dev()
