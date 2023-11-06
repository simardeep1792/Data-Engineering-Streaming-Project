# Importing necessary libraries and modules
import requests
import json
import time
import hashlib
from confluent_kafka import Producer

# Constants and configuration
API_ENDPOINT = "https://randomuser.me/api/?results=1"
KAFKA_BOOTSTRAP_SERVERS = ['kafka_broker_1:19092','kafka_broker_2:19093','kafka_broker_3:19094']
KAFKA_TOPIC = "names_topic"  
PAUSE_INTERVAL = 10  
STREAMING_DURATION = 120

def retrieve_user_data(url=API_ENDPOINT) -> dict:
    """Fetches random user data from the provided API endpoint."""
    response = requests.get(url)
    return response.json()["results"][0]

def transform_user_data(data: dict) -> dict:
    """Formats the fetched user data for Kafka streaming."""
    return {
        "name": f"{data['name']['title']}. {data['name']['first']} {data['name']['last']}",
        "gender": data["gender"],
        "address": f"{data['location']['street']['number']}, {data['location']['street']['name']}",  
        "city": data['location']['city'],
        "nation": data['location']['country'],  
        "zip": encrypt_zip(data['location']['postcode']),  
        "latitude": float(data['location']['coordinates']['latitude']),
        "longitude": float(data['location']['coordinates']['longitude']),
        "email": data["email"]
    }

def encrypt_zip(zip_code):  
    """Hashes the zip code using MD5 and returns its integer representation."""
    zip_str = str(zip_code)
    return int(hashlib.md5(zip_str.encode()).hexdigest(), 16)

def configure_kafka(servers=KAFKA_BOOTSTRAP_SERVERS):
    """Creates and returns a Kafka producer instance."""
    settings = {
        'bootstrap.servers': ','.join(servers),
        'client.id': 'producer_instance'  
    }
    return Producer(settings)

def publish_to_kafka(producer, topic, data):
    """Sends data to a Kafka topic."""
    producer.produce(topic, value=json.dumps(data).encode('utf-8'), callback=delivery_status)
    producer.flush()

def delivery_status(err, msg):
    """Reports the delivery status of the message to Kafka."""
    if err is not None:
        print('Message delivery failed:', err)
    else:
        print('Message delivered to', msg.topic(), '[Partition: {}]'.format(msg.partition()))

def initiate_stream():
    """Initiates the process to stream user data to Kafka."""
    kafka_producer = configure_kafka()
    for _ in range(STREAMING_DURATION // PAUSE_INTERVAL):
        raw_data = retrieve_user_data()
        kafka_formatted_data = transform_user_data(raw_data)
        publish_to_kafka(kafka_producer, KAFKA_TOPIC, kafka_formatted_data)
        time.sleep(PAUSE_INTERVAL)

if __name__ == "__main__":
    initiate_stream()
