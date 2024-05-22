from fastapi import FastAPI

from .db_setup import get_db
from .file_mgt import controllers


app = FastAPI()
app.include_router(controllers.router)
