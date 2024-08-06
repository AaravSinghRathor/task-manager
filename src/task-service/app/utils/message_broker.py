import json
import os
import time
from typing import Any

import pika
import pika.exceptions
from pika.adapters.blocking_connection import BlockingChannel

from app.utils.logger import logger

channel: BlockingChannel = None  # type: ignore


def get_rabbitmq_connection() -> Any:
    # rabbitmq connection
    max_count = 7
    count = 0
    while count < max_count:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host="rabbitmq",
                    port=5672,
                    credentials=pika.PlainCredentials(
                        os.getenv("RABBITMQ_USER", ""),
                        os.getenv("RABBITMQ_PASSWORD", ""),
                    ),
                    heartbeat=60
                )
            )
            logger.info("New rabbitmq connection created")
            return connection
        except pika.exceptions.AMQPConnectionError:
            count += 1
            logger.info("Connection failed, retrying in 5 seconds...")
            time.sleep(5)
    return None


def get_rabbitmq_channel() -> BlockingChannel | None:
    global channel
    if not channel or channel.is_closed:
        connection = get_rabbitmq_connection()
        if not connection:
            return None
        channel = connection.channel()
        channel.queue_declare(queue="notification_queue", durable=True)
    return channel


def close_rabbitmq_channel() -> None:
    global channel
    try:
        channel.close()
    except Exception:
        logger.error("error occurred while closing channel")


def publish(message: Any) -> None:
    global channel
    if not channel:
        try:
            get_rabbitmq_channel()
        except Exception as e:
            logger.error(f"Failed to create channel: {e}")
            channel = None  # type: ignore
    try:
        channel.basic_publish(
            exchange="",
            routing_key="notification_queue",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )
    except pika.exceptions.ConnectionClosedByBroker:
        logger.warn("Connection closed by broker, attempting to reconnect...")
        channel = None  # type: ignore
        try:
            get_rabbitmq_channel()
            channel.basic_publish(
                exchange="",
                routing_key="notification_queue",
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                ),
            )
        except Exception as e:
            channel = None  # type: ignore
            logger.error(f"Failed to publish message: {e}")
    except pika.exceptions.StreamLostError:
        logger.warn("Stream connection lost, attempting to reconnect...")
        channel = None  # type: ignore
        try:
            get_rabbitmq_channel()
            channel.basic_publish(
                exchange="",
                routing_key="notification_queue",
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                ),
            )
        except Exception as e:
            channel = None  # type: ignore
            logger.error(f"Failed to publish message: {e}")
    except Exception as e:
        logger.error(f"Failed to publish message: {e}")
        channel = None  # type: ignore
