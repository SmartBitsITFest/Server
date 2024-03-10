from fastapi import FastAPI

from controllers.controller import router

app = FastAPI()

app.include_router(router) 