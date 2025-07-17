from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    MODEL_NAME: str = "gpt-3.5-turbo"
    
    class Config:
        env_file = ".env"

settings = Settings() # pyright: ignore
