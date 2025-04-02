from pathlib import Path

from pydantic import BaseModel, NatsDsn, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class JWTConfig(BaseModel):
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30


class SecurityConfig(BaseModel):
    private_key: Path = BASE_DIR / "app" / "core" / "certs" / "private_key.pem"
    public_key: Path = BASE_DIR / "app" / "core" / "certs" / "public_key.pem"
    jwt: JWTConfig = JWTConfig()


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


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int
    max_connections: int = 10


class NatsConfig(BaseModel):
    url: NatsDsn
    idempotency_key_expire: int = 24 * 60 * 60


class SMTPConfig(BaseModel):
    host: str
    port: int
    username: str
    password: SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="ENV_",
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file_encoding="utf-8",
    )

    db: DatabaseConfig
    redis: RedisConfig
    nats: NatsConfig
    smtp: SMTPConfig
    security: SecurityConfig = SecurityConfig()
    frontend_url: str


settings = Settings()  # type: ignore


print(settings.frontend_url)
