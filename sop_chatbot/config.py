import os

from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()


VERSION = '0.1.0'
APP = 'SOPs Chatbot'
DESCRIPTION = 'This is a chatbot that will receive Standard Operation Procedures, manuals, and other documents and will be able to answer questions about them.'


DEBUG = os.getenv('DEBUG', 'False').capitalize() == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'This is my secret key')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/sops')
TEST_MONGO_URI = os.getenv(
    'TEST_MONGO_URI', 'mongodb://localhost:27017/sops_test'
)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'This is my Gemini API key')
