import asyncio

from pymongo import IndexModel

from .. import session


async def create_indexes():
    await asyncio.gather(
        session.db.users.create_indexes(
            [
                IndexModel([('email', 1)]),
                IndexModel([('registration', 1)]),
                IndexModel([('name', 'text')]),
            ]
        ),
        session.db.companies.create_indexes(
            [
                IndexModel([('name', 'text')]),
                IndexModel([('registration', 1)]),
            ]
        ),
        session.db.departments.create_indexes(
            [
                IndexModel([('name', 'text')]),
                IndexModel([('registration', 1)]),
            ]
        ),
    )


async def run():
    await create_indexes()
