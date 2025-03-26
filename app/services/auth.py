import bcrypt
from itsdangerous import URLSafeTimedSerializer

from config import settings


serializer = URLSafeTimedSerializer(secret_key=settings.private_key.read_text())


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def validate_password(password: str, hash_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hash_password)
