from pathlib import Path
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent
ENV_FILE = str(BASE_DIR / ".env")
ENV_TEMPLATE_FILE = str(BASE_DIR / ".env.template")


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool
    pool_size: int
    max_overflow: int
    naming_convention: dict = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[ENV_TEMPLATE_FILE, ENV_FILE],
        env_prefix="ENV_",
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file_encoding="utf-8",
    )

    db: DatabaseConfig


settings = Settings()  # type: ignore
