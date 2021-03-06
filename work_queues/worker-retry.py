#!/usr/bin/env python
import pika
import time
import json

from retry import retry

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

    message = json.loads(body)

    result = message["arg_first"] + message["arg_second"]

    print(" [x] Result: %s + %s = %s" % ( message["arg_first"], message["arg_second"], result))

    time.sleep(1)

    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


@retry(Exception, delay=5, jitter=(1, 3))
def main():
    credentials = pika.PlainCredentials('mquser', 'mquser')
    parameters = pika.ConnectionParameters('rabbitmq-lb', 5672, '/app', credentials)

    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()

    channel.queue_declare(queue='worker_queue1', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='worker_queue1', on_message_callback=callback)

    channel.start_consuming()

main()
