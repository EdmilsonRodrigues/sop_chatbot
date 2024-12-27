import os
from collections.abc import AsyncGenerator, Callable
from datetime import datetime
from importlib import import_module

from .. import session
from ..config import settings

MAIN_VERSION = int(settings.VERSION.split('.')[0])
SUB_VERSION = int(settings.VERSION.split('.')[1])
PATCH = int(settings.VERSION.split('.')[2])


async def run_migrations():
    async for migration in get_migrations():
        migration_name = await migration()
        print(f'Migration {migration_name} ran successfully')
        await session.db.migrations.insert_one(
            {'name': migration_name, 'run_at': datetime.now()}
        )
    print('All migrations ran successfully')


async def get_migrations() -> AsyncGenerator[Callable]:
    all_migrations = [
        os.path.join('migrations', f)
        for f in os.listdir('migrations')
        if f.startswith('migration_')
    ]
    ran_migrations = set(await session.db.migrations.find().distinct('name'))
    for migration in all_migrations:
        version = int(migration.split('_')[1])
        subversion = int(migration.split('_')[2])
        patch = int(migration.split('_')[3].split('.')[0])
        if version > MAIN_VERSION:
            continue
        elif version == MAIN_VERSION and subversion > SUB_VERSION:
            continue
        elif (
            version == MAIN_VERSION
            and subversion == SUB_VERSION
            and patch > PATCH
        ):
            continue
        migration = import_module(
            migration.replace('/', '.').replace('.py', '')
        )
        if migration.__name__ not in ran_migrations:
            yield migration.run


if __name__ == '__main__':
    import asyncio

    asyncio.run(run_migrations())
