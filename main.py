import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel

from config import APP, DEBUG, DESCRIPTION, VERSION
from routes.api import router as api_router
from migrations.indexes import create_indexes
from migrations.migrations import run_migrations


tags_info = [
    {"name": "Version", "description": "Version information"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.gather(create_indexes(), run_migrations())
    yield
    # Application shutdown


app = FastAPI(
    version=VERSION,
    title=APP,
    description=DESCRIPTION,
    debug=DEBUG,
    lifespan=lifespan,
    openapi_tags=tags_info,
)

app.include_router(api_router)


class VersionInfo(BaseModel):
    version: str


@app.get("/", response_model=VersionInfo, tags=["Version"])
def version():
    return {"version": VERSION}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
