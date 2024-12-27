from motor.motor_asyncio import AsyncIOMotorClient

from sop_chatbot.config import MONGO_URI

db = AsyncIOMotorClient(MONGO_URI).get_database()
