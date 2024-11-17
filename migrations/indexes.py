import asyncio
from session import db
from pymongo import IndexModel


async def create_indexes():
    await asyncio.gather(
        db.users.create_indexes(
            [
                IndexModel([("email", 1)]),
                IndexModel([("registration", 1)]),
                IndexModel([("name", "text")]),
            ]
        ),
        db.companies.create_indexes(
            [
                IndexModel([("name", "text")]),
                IndexModel([("registration", 1)]),
            ]
        ),
        db.departments.create_indexes(
            [
                IndexModel([("name", "text")]),
                IndexModel([("registration", 1)]),
            ]
        ),
    )


async def run():
    await create_indexes()
