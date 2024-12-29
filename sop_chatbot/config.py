import os

from pydantic_settings import BaseSettings, SettingsConfigDict

os.chdir(os.path.dirname(__file__))


class Settings(BaseSettings):
    VERSION: str = '0.1.0'
    APP: str = 'SOPs Chatbot'
    DESCRIPTION: str = ' '.join(
        (
            'This is a chatbot that will receive Standard',
            'Operation Procedures, manuals, and other documents',
            'and will be able to answer questions about them.',
        )
    )
    DEBUG: bool = False
    SECRET_KEY: str = 'This is my secret key'
    MONGO_URI: str = 'mongodb://localhost:27017/sops'
    TEST_MONGO_URI: str = 'mongodb://localhost:27017/sops_test'
    GEMINI_API_KEY: str = 'This is my Gemini API key'
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


settings = Settings()
