import asyncio
import json
import os

import aio_pika

from app.utils.logger import logger
from app.utils.new_email import send_email_async


async def process_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        try:
            logger.info("Processing message...")
            # Simulate message processing
            message_body = json.loads(message.body)
            operation = message_body["operation"]
            task = message_body["task"]
            email = message_body.get("email")
            if operation == "create":
                await send_email_async("Task created: {}".format(task), email)
            elif operation == "update":
                await send_email_async("Task updated: {}".format(task), email)
            elif operation == "delete":
                await send_email_async("Task with ID: {} deleted".format(task), email)
            elif operation == "complete":
                await send_email_async("Task mark as completed: {}".format(task), email)
            else:
                logger.warn(f"Unsupported operation: {operation}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise  # This will trigger a retry if you are using a retry mechanism


async def consume() -> None:
    connection = None
    while True:
        try:
            if connection is None or connection.is_closed:
                # Only create a new connection if none exists or the previous one is closed
                connection = await aio_pika.connect_robust(
                    host="rabbitmq",
                    login=os.getenv("RABBITMQ_USER", ""),
                    password=os.getenv("RABBITMQ_PASSWORD", ""),
                )
                logger.info("Connected to RabbitMQ.")

            channel = await connection.channel()
            queue = await channel.declare_queue("notification_queue", durable=True)
            logger.info("Waiting for messages in queue 'notification_queue'.")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    # Process each message in a background task
                    asyncio.create_task(process_message(message))

        except (aio_pika.exceptions.AMQPConnectionError, ConnectionResetError) as e:
            logger.error(f"Connection lost: {e}. Reconnecting...")
            connection = None  # Ensure we create a new connection on the next iteration
            await asyncio.sleep(5)  # Delay before retrying the connection

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume())
