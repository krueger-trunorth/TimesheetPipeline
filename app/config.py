'''
----------------------------------------------------------------------------------------------------------------------
                                                App Config
----------------------------------------------------------------------------------------------------------------------
Shared runtime flags for the TruNorth Timesheet dashboard.
Used by dev mode to bypass Docker and the attached database during UI work.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries
import os


# config helpers
def is_db_disabled() -> bool:
    return os.getenv("DISABLE_DB", "").lower() in {"1", "true", "yes"}


def is_dev_mode() -> bool:
    return is_db_disabled()
