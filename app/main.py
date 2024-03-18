from fastapi import FastAPI

import app.routes as routes
from app.database import create_db_and_tables

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
            "name": "Checks",
            "description": "Operations for testing records"
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

# Attach all the routes we serve.
app.include_router(routes.router)
