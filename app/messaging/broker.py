import json
from aiosmtplib.errors import SMTPException
from core.config import settings
from core.mail import send_confirmation_email
from faststream.nats import JStream
from faststream.nats.fastapi import Logger, NatsMessage, NatsRouter
from nats.js.api import RetentionPolicy, StorageType
from pydantic import BaseModel, Json

router = NatsRouter(str(settings.nats.url))

stream = JStream(
    name="mail_sending_queue",
    subjects=["email.confirm"],
    storage=StorageType.FILE,
    retention=RetentionPolicy.WORK_QUEUE,
    max_msg_size=10 * 1024 * 1024,
    duplicate_window=10,
)


class EmailConfirm(BaseModel):
    to_email: str
    token: str


@router.subscriber(subject="postgres.public.outbox")
async def handler(msg: dict[str, dict], raw_msg: NatsMessage, logger: Logger):
    data = json.loads(msg["payload"]["after"]["payload"])

    to_email = data["to_email"]
    token = data["token"]
    try:
        await send_confirmation_email(to_email, token)
        await raw_msg.ack()
    except SMTPException as e:
        logger.error(f"SMTP error: {e}")
        await raw_msg.nack(delay=30)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def pub_confirmation_email_to_broker(
    to_email: str,
    token: str,
    message_id: str,
):
    await router.broker.publish(
        message={"to_email": to_email, "token": token},
        subject="email.confirm",
        headers={"Nats-Msg-Id": message_id},
    )
