
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ai-webapp"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    secret_key: str = "uchiha-secret-key"

    db_host: str = "localhost"
    db_port: int = 5434
    db_name: str = "uchiha_db"
    db_user: str = "uchiha_itachi"
    db_password: str = "sharingan"

    openai_api_key: str | None = None
    tavily_api_key: str | None = None

    vector_dir: str = "vectorstore"
    upload_dir: str = "uploads"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def db_uri(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()
