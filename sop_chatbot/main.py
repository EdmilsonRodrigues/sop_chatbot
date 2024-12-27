import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from .config import APP, DEBUG, DESCRIPTION, VERSION
from .migrations.indexes import create_indexes
from .migrations.migrations import run_migrations
from .routes.api import router as api_router

os.chdir(os.path.dirname(__file__))

tags_info = [
    {'name': 'Version', 'description': 'Version information'},
    {'name': 'Auth', 'description': 'Authentication related operations'},
    {'name': 'Admin', 'description': 'Operations for administrators'},
    {'name': 'Users', 'description': 'Users related operations'},
    {
        'name': 'Admin: Users',
        'description': 'Users related operations for administrators',
    },
    {'name': 'Companies', 'description': 'Companies related operations'},
    {
        'name': 'Admin: Companies',
        'description': 'Companies related operations for administrators',
    },
    {'name': 'Departments', 'description': 'Departments related operations'},
    {
        'name': 'Admin: Departments',
        'description': 'Departments related operations for administrators',
    },
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


@app.get('/', response_model=VersionInfo, tags=['Version'])
def version():
    return {'version': VERSION}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
