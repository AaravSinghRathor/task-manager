import json
import os
import sys
import time
from typing import Any

import pika
import pika.exceptions
from pika.adapters.blocking_connection import BlockingChannel

from app.utils.email import send_email


def send_notification(
    method: Any, channel: BlockingChannel, email: None | str, message: str
) -> None:
    if email:
        success = send_email(email, message)
        if not success:
            print("error")
            channel.basic_nack(delivery_tag=method.delivery_tag)
        else:
            channel.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print(message)


def callback(ch: Any, method: Any, properties: Any, body: Any) -> None:
    message = json.loads(body)

    operation = message["operation"]
    task = message["task"]
    email = message.get("email")
    if operation == "create":
        send_notification(method, ch, email, "Task created: {}".format(task))
    elif operation == "update":
        send_notification(method, ch, email, "Task updated: {}".format(task))
    elif operation == "delete":
        send_notification(method, ch, email, "Task with ID: {} deleted".format(task))
    elif operation == "complete":
        send_notification(method, ch, email, "Task mark as completed: {}".format(task))


def get_rabbitmq_connection() -> Any:
    # rabbitmq connection
    time.sleep(30)
    max_count = 5
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
                )
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            count += 1
            print("Connection failed, retrying in 5 seconds...")
            time.sleep(5)
    return None


def main() -> None:
    connection = get_rabbitmq_connection()
    if not connection:
        print("Could not establish connection with RabbitMQ. Exiting....")
        return
    channel = connection.channel()
    channel.queue_declare(queue="notification_queue", durable=True)

    channel.basic_consume(queue="notification_queue", on_message_callback=callback)

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
