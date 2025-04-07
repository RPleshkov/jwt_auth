from aiosmtplib.errors import SMTPException
from core.config import settings
from core.mail import send_confirmation_email
from core.redis_client import RedisHelper
from core.security import serializer
from faststream.nats import DeliverPolicy
from faststream.nats.fastapi import Logger, NatsMessage, NatsRouter
from utils.helpers import handle_failed_message

from .streams import email_stream

router = NatsRouter(str(settings.nats.url))


@router.subscriber(
    subject="email.send",
    no_ack=True,
    stream=email_stream,
    deliver_policy=DeliverPolicy.ALL,
)
async def handler(msg: str, raw_msg: NatsMessage, logger: Logger):
    confirmation_token = serializer.dumps(msg)

    try:
        await send_confirmation_email(msg, confirmation_token)
        await raw_msg.ack()

    except SMTPException as e:
        logger.error(f"SMTP error: {e}")

        msg_id = raw_msg.headers["Nats-Msg-Id"]

        async with RedisHelper() as redis:
            attempts = await redis.client.get(msg_id)  # type: ignore
            if attempts is None:
                attempts = 1
            else:
                attempts = int(attempts) + 1

            await redis.client.set(msg_id, attempts, ex=10)  # type: ignore

            if attempts == 3:
                payload = handle_failed_message(msg, str(e))

                await router.broker.publish(
                    message=payload,
                    subject="dead.email.send",
                    stream="dead-letters-stream",
                    headers={"Nats-Msg-Id": msg_id},
                )

                await raw_msg.ack()
            else:
                await raw_msg.nack(delay=5)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await raw_msg.nack(delay=5)
