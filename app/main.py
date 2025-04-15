from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import Session
from uvicorn.logging import ColourizedFormatter

from app.database import create_db
import app.routes as routes
from app.settings_env import get_env_settings
from app.settings import Settings
from app.utility.vice_county.vc_checker import VcChecker
from app.user.user_repo import UserRepo


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform startup tasks.
    env = get_env_settings()

    # Initialise logging.
    # I have an unexplained problem that, when running on the Kubernetes
    # cluster, Uvicorn could output logs but not my application. To work around
    # this, I am piggy backing on Uvicorn's logging.
    logger = logging.getLogger("uvicorn")
    logger.setLevel(env.log_level.upper())
    console_formatter = ColourizedFormatter(
        fmt="{asctime} {levelprefix:<8} {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        use_colors=True)
    if len(logger.handlers) == 0:
        logger.addHandler(logging.StreamHandler())
    logger.handlers[0].setFormatter(console_formatter)

    # Make Uvicorn access logs consistent with root logger.
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.setLevel(env.log_level.upper())
    if len(access_logger.handlers) == 0:
        access_logger.addHandler(logging.StreamHandler())
    access_logger.handlers[0].setFormatter(console_formatter)

    logger.info('Record Cleaner starting...')

    # Initialise database.
    engine = create_db(env)

    # Initialise settings.
    settings = Settings(engine)

    # Create the initial user.
    with Session(engine) as session:
        repo = UserRepo(session)
        repo.create_initial_user(env)

    # Load the county data once.
    VcChecker.load_data()

    context = {'engine': engine, 'settings': settings}
    # Store the context so it is available in unit tests.
    app.context = context

    # Yield the context which will be available in request.state.
    yield context

    # Perform shutdown tasks.
    logger.info('Record Cleaner shutting down...')


# Instantiate the app.
app = FastAPI(
    lifespan=lifespan,
    title="Record Cleaner Service",
    summary="Service for checking species records against the record "
    "cleaner rules.",
    version="3.0.0-beta02",
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
        {
            "name": "Counties",
            "description": "Operations on counties"
        },
        {
            "name": "Users",
            "description": "Operations on users (admin only)"
        }
    ]
)


# Add middleware.

@app.middleware("http")
async def maintenance_middleware(request: Request, call_next):
    """Middleware to handle maintenance mode."""
    if (
        request.state.settings.db.maintenance_mode and
        request['path'] != '/' and
        request['path'] != '/token' and
        request['path'] != '/maintenance' and
        request['path'] != '/docs' and
        request['path'] != '/openapi.json'
    ):
        data = {"message": request.state.settings.db.maintenance_message}
        return JSONResponse(
            content=jsonable_encoder(data),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # Process as normal
    response = await call_next(request)
    return response

# Attach all the routes we serve.
app.include_router(routes.router)
