import pika, json, time, os
from dotenv import load_dotenv

# Load the stored environment variables
load_dotenv()

connection_params = pika.ConnectionParameters(
    host='docker-taskyflow-microservice-rabbitmq-container-1',
    port=5672,
    virtual_host='/',
    credentials=pika.PlainCredentials(username='taskyapp', password='1345'),
    heartbeat=600,
)

def establish_connection():
    while True:
        try:
            connection = pika.BlockingConnection(connection_params)
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("Connection failed. Retrying...")
            time.sleep(5)

connection = establish_connection()
channel = connection.channel()
channel.queue_declare(queue='task', durable=True)

def publish_to_notification(method, body):
    global channel
    try:
        properties = pika.BasicProperties(
            content_type='application/json', delivery_mode=2)
        channel.basic_publish(
            exchange='',
            routing_key='task',
            body=json.dumps(body),
            properties=properties   # Make the message persistent
        )
  
    except pika.exceptions.AMQPChannelError as channel_error:
        print(f"AMQP Channel Error: {channel_error}")
        # Re-establish the connection
        connection = establish_connection()
        channel = connection.channel()
        channel.queue_declare(queue='task', durable=True)
    except pika.exceptions.AMQPConnectionError as connection_error:
        print(f"AMQP Connection Error: {connection_error}")
        # Re-establish the connection
        connection = establish_connection()
        channel = connection.channel()
        channel.queue_declare(queue='task', durable=True)       