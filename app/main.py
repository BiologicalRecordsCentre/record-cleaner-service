from fastapi import FastAPI

import app.routes as routes

# Instantiate the app.
app = FastAPI(
    title="Record Cleaner Service",
    summary="Service for checking species records against the record "
    "cleaner rules",
    version="0.0.1",
    openapi_tags=[
        {
            "name": "species",
            "description": "Operations on species"
        },
        {
            "name": "counties",
            "description": "Operations on counties"
        },
        {
            "name": "rules",
            "description": "Operations on rules"
        },
        {
            "name": "users",
            "description": "Operations on users"
        }
    ]
)
# Attach all the routes we server.
app.include_router(routes.router)
