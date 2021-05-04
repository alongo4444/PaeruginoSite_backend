from fastapi import FastAPI, Depends
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware;
import uvicorn
# from fastapi.staticfiles import StaticFiles
# from starlette.staticfiles import StaticFiles
from app.api.api_v1.routers.genes import genes_router
from app.api.api_v1.routers.isolation import isolation_router
from app.api.api_v1.routers.strains import strains_router
from app.api.api_v1.routers.defense_systems import defense_systems_router
from app.api.api_v1.routers.statistics import statistics_router
from app.db.session import SessionLocal
from app.api.api_v1.routers.cluster import cluster_router
import os
from dotenv import load_dotenv
load_dotenv()



app = FastAPI(
    title=os.getenv('PROJECT_NAME'), docs_url="/api/docs", openapi_url="/api"
)

# app.mount("/static", StaticFiles(directory="static"), name="static")

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


@app.get("/api/v1/tables")
async def example_task():
    # request.state.db

    return {"message": "success"}


# Routers
# app.include_router(
#     users_router,
#     prefix="/api/v1",
#     tags=["users"],
#     dependencies=[Depends(get_current_active_user)],
# )
# app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(genes_router, prefix="/api/v1/genes", tags=["genes"])
app.include_router(strains_router, prefix="/api/v1/strains", tags=["strains"])
app.include_router(cluster_router, prefix="/api/v1/cluster", tags=["cluster"])
app.include_router(statistics_router, prefix="/api/v1/statistics", tags=["statistics"])
app.include_router(defense_systems_router, prefix="/api/v1/defense", tags=["defense_systems"])
app.include_router(isolation_router, prefix="/api/v1/isolation", tags=["isolation"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", reload=True, reload_dirs=["./api", "./db"], port=8800)
