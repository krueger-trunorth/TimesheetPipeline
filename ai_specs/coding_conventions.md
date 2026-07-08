# Python Conventions
Please strictly adhere to these conventions when generating code; this is intended for easy observability into the AI's decision making and for easier understanding of generated code.

- use type annotations when available
- follow principle of least priveledge
- use short, single purpose functions 
- follow OOP when possible (dasboard pages, complex data objects)
- use DESCRIPTIVE comments at the start of each file:
example:
```
''' 
----------------------------------------------------------------------------------------------------------------------
                                                Data Import Functions   
----------------------------------------------------------------------------------------------------------------------
This file contains the data import functions for the TruNorth Timesheet datatables.
Using SQLAlchemy, we can pull data from the database and return a pandas dataframe.
----------------------------------------------------------------------------------------------------------------------
'''
```

- use SHORT, SIMPLE comments for each logical section in code:
example:
```
# import libraries

# import pages

# app definitions

# page definitions

# dashboard layout callback 
```