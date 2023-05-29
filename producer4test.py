import json
import os

from confluent_kafka import Producer
from dotenv import load_dotenv

load_dotenv()

KAFKA_HOST = os.getenv('KAFKA_HOST', default='host.docker.internal')
KAFKA_PORT = os.getenv('KAFKA_PORT', default='19092')


p = Producer({'bootstrap.servers': f'{KAFKA_HOST}:{KAFKA_PORT}'})
data = {'id': 2, 'name': 'NEW NAME!4444444'}
delete_data = {'id': 1}
mess = json.dumps(data)
delete_mess = json.dumps(delete_data)
p.produce('updates', value=mess.encode('utf-8'))
p.produce('deletions', value=delete_mess.encode('utf-8'))
p.flush()
