from fastapi import FastAPI, Depends
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware;
import uvicorn

from app.api.api_v1.routers.genes import genes_router
from app.api.api_v1.routers.strains import strains_router

from app.core import config
from app.db.session import SessionLocal
from app.core.celery_app import celery_app
from app import tasks
from app.api.api_v1.routers.users import users_router
from app.api.api_v1.routers.auth import auth_router
from app.core.auth import get_current_active_user


app = FastAPI(
    title=config.PROJECT_NAME, docs_url="/api/docs", openapi_url="/api"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    request.state.db.close()
    return response


# @app.get("/api/v1")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/api/v1/task")
# async def example_task():
#     celery_app.send_task("app.tasks.example_task", args=["Hello World"])
#
#     return {"message": "success"}

@app.get("/api/v1/tables")
async def example_task(request):
    request.state.db

    return {"message": "success"}


# Routers
# Routers
app.include_router(
    users_router,
    prefix="/api/v1",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)],
)
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(genes_router, prefix="/api/v1", tags=["genes"])
app.include_router(strains_router, prefix="/api/v1", tags=["strains"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", reload=True, port=8800)
