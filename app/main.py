from fastapi import FastAPI, Depends
from starlette.requests import Request
import uvicorn

from app.api.api_v1.routers.genes import genes_router
from app.api.api_v1.routers.strains import strains_router

# from app.api.api_v1.routers.auth import auth_router
from app.core import config
from app.db.session import SessionLocal
from app.core.celery_app import celery_app
from app import tasks

app = FastAPI(
    title=config.PROJECT_NAME, docs_url="/api/docs", openapi_url="/api"
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    request.state.db.close()
    return response


@app.get("/api/v1/tables")
async def example_task(request):
    request.state.db

    return {"message": "success"}


# Routers

app.include_router(genes_router, prefix="/api/v1", tags=["genes"])
app.include_router(strains_router, prefix="/api/v1", tags=["strains"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8880)
