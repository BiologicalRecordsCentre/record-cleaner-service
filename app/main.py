from fastapi import FastAPI

import app.routes as routes
from app.database import create_db_and_tables
from app.utilities.vice_counties.vc_checker import VcChecker

# Instantiate the app.
app = FastAPI(
    title="Record Cleaner Service",
    summary="Service for checking species records against the record "
    "cleaner rules",
    version="0.0.1",
    openapi_tags=[
        {
            "name": "Service",
            "description": "Basic information"
        },
        {
            "name": "Validate",
            "description": "Operations to validate record data."
        },
        {
            "name": "Verify",
            "description": "Operations to verify records against rules."
        },
        {
            "name": "Species",
            "description": "Operations on species"
        },
        {
            "name": "Rules",
            "description": "Operations on rules"
        },
        {
            "name": "Indicia",
            "description": "Operations on the Indicia warehouse"
        },
        {
            "name": "Species Cache",
            "description": "Operations on the species cache"
        },
        {
            "name": "Counties",
            "description": "Operations on counties"
        },
        {
            "name": "Users",
            "description": "Operations on users"
        }
    ]
)

# Create the database tables.
create_db_and_tables()

# Load the vice county checker fiiles.
VcChecker.load_data()

# Attach all the routes we serve.
app.include_router(routes.router)
