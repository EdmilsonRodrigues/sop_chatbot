from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_CONNECTION_URL, MONGO_DATABASE


db = AsyncIOMotorClient(MONGO_CONNECTION_URL)[MONGO_DATABASE]
