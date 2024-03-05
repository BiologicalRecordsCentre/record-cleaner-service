from fastapi import FastAPI

import app.routes as routes

# Instantiate the app.
app = FastAPI()
# Attach all the routes we server.
app.include_router(routes.router)
