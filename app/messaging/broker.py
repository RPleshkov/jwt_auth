from aiosmtplib.errors import SMTPException
from core.config import settings
from core.mail import send_confirmation_email
from core.security import serializer
from faststream.nats import DeliverPolicy, JStream
from faststream.nats.fastapi import Logger, NatsMessage, NatsRouter
from nats.js.api import RetentionPolicy, StorageType

router = NatsRouter(str(settings.nats.url))

stream = JStream(
    name="email-stream",
    subjects=["email.>"],
    storage=StorageType.FILE,
    retention=RetentionPolicy.WORK_QUEUE,
    max_msgs=100,
    max_msg_size=10 * 1024 * 1024,
    duplicate_window=5 * 60,
)


@router.subscriber(
    subject="email.send",
    no_ack=True,
    stream=stream,
    deliver_policy=DeliverPolicy.ALL,
)
async def handler(msg: str, raw_msg: NatsMessage, logger: Logger):
    confirmation_token = serializer.dumps(msg)

    try:
        await send_confirmation_email(msg, confirmation_token)
        await raw_msg.ack()
    except SMTPException as e:
        logger.error(f"SMTP error: {e}")
        await raw_msg.nack(delay=30)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
