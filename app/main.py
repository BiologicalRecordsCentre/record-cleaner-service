from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.database import engine
import app.routes as routes
from app.settings import settings
from app.utility.vice_county.vc_checker import VcChecker
from app.user.user_repo import UserRepo

# Instantiate the app.
app = FastAPI(
    title="Record Cleaner Service",
    summary="Service for checking species records against the record "
    "cleaner rules.",
    version="0.0.12",
    contact={
        "name": "Biological Records Centre at UK Centre for Ecology & Hydrology",
        "url": "https://www.ceh.ac.uk/our-science/projects/biological-records-centre",
        "email": "brc@ceh.ac.uk",
    },
    description="""This is a web interface which allows you to experiment with
the record cleaner service. It is intended for developers and not for general
use. To use all but the base endpoint, which returns status information, you
need a username and password to be created by an administrator.

To authenticate, click a padlock icon, enter your username and password, and
click the Authorize button followed by the Close buttion in the subsequent
dialog. The padlock icon will then be closed and you will retain authentication
for 15 minutes. Some services, such as user management, are only available to 
admin users.

To try an endpoint, expand it by clicking the down arrow at the right hand end
of its title bar and click the Try It Out button that appears below. The
request may require a parameter or a body to be specified. When ready, click
the Execute button to sent the request. The response will appear below.""",
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
        # {
        #     "name": "Counties",
        #     "description": "Operations on counties"
        # },
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
        request['path'] != '/' and
        request['path'] != '/token' and
        request['path'] != '/maintenance' and
        request['path'] != '/docs' and
        request['path'] != '/openapi.json'
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

# Create the initial user.
with Session(engine) as session:
    repo = UserRepo(session)
    repo.create_initial_user()

# Attach all the routes we serve.
app.include_router(routes.router)
