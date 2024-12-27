from config import MONGO_URI
from motor.motor_asyncio import AsyncIOMotorClient

db = AsyncIOMotorClient(MONGO_URI).get_database()
