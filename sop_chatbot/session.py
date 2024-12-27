from motor.motor_asyncio import AsyncIOMotorClient

from .config import MONGO_URI

db = AsyncIOMotorClient(MONGO_URI).get_database()
