from faststream import FastStream, Logger
from faststream.nats import JStream, NatsBroker, NatsMessage
from nats.js.api import RetentionPolicy, StorageType
from pydantic import BaseModel
from aiosmtplib.errors import SMTPException
from redis.exceptions import RedisError

from core.redis_client import RedisHelper
from core.config import settings
from core.mail import send_confirmation_email


broker = NatsBroker(str(settings.nats.url))
app = FastStream(broker)

stream = JStream(
    name="mail_sending_queue",
    subjects=["email.confirm"],
    storage=StorageType.FILE,
    retention=RetentionPolicy.WORK_QUEUE,
    max_msg_size=10 * 1024 * 1024,
    duplicate_window=2,
)


class EmailConfirm(BaseModel):
    to_email: str
    token: str
    message_id: str


@broker.subscriber("email.confirm", stream=stream)
async def handler(msg: EmailConfirm, raw_msg: NatsMessage, logger: Logger):
    idempotency_key = f"email:{msg.message_id}"
    try:
        async with RedisHelper() as redis:
            if await redis.client.get(idempotency_key):  # type: ignore
                logger.info(f"Duplicate message {msg.message_id}, skipping")
                await raw_msg.ack()
                return

            logger.info(
                f"Processing email to {msg.to_email} with message ID {msg.message_id}"
            )
            try:
                await send_confirmation_email(msg.to_email, msg.token)
                await redis.client.set(  # type: ignore
                    idempotency_key, "done", ex=settings.nats.idempotency_key_expire
                )
                await raw_msg.ack()
            except SMTPException as e:
                logger.error(f"SMTP error: {e}")
                await raw_msg.nack(delay=30)

    except RedisError as e:
        logger.error(f"Redis error: {e}")
        await raw_msg.nack(delay=30)

    except Exception as e:
        logger.error(f"Unexpected error for message ID {msg.message_id}: {e}")
        await raw_msg.nack(delay=30)


async def pub_confirmation_email_to_broker(
    to_email: str,
    token: str,
    message_id: str,
):
    async with broker:
        await broker.publish(
            {"to_email": to_email, "token": token, "message_id": message_id},
            subject="email.confirm",
        )
