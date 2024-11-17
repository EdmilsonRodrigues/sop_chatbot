import asyncio
from session import db


async def create_indexes():
    await asyncio.gather(
        db.users.create_indexes(
            [{"key": {"email": 1}}, {"key": {"register": 1}}, {"key": {"name": "text"}}]
        ),
        db.companies.create_indexes(
            [{"key": {"name": "text"}}, {"key": {"register": 1}}]
        ),
        db.departments.create_indexes(
            [{"key": {"name": "text"}}, {"key": {"register": 1}}]
        ),
    )


async def run():
    await create_indexes()
