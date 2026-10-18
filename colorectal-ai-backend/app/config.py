from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    max_upload_mb: int = 10
    models_dir: Path = BASE_DIR / "models"
    upload_dir: Path = BASE_DIR / "uploads"
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")
settings = Settings()
