from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import app.routes as routes
from app.settings import settings
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


# Add middleware.


@app.middleware("http")
async def maintenance_middleware(request: Request, call_next):
    """Middleware to handle maintenance mode."""
    if (
        settings.db.maintenance_mode and
        request['path'] != "/maintenance" and
        request['path'] != "/"
    ):
        data = {"message": settings.db.maintenance_message}
        return JSONResponse(
            content=jsonable_encoder(data),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # Process as normal
    response = await call_next(request)
    return response

# Load the county data once. Maybe find a better place for this.
VcChecker.load_data()

# Attach all the routes we serve.
app.include_router(routes.router)
