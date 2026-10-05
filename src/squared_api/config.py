from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    jwt_secret_key: str
    access_token_minutes: int = 60 * 24 * 7
    environment: str = "development"


settings = Settings()