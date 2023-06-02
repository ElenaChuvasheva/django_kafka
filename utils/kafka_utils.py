import json
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock, Thread, active_count
from typing import Any, Callable

from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from django.conf import settings

from api.serializers import SomeModelSerializer, SomeModelUpCreateSerializer
from application.models import SomeModel

lock = Lock()

client_conf = {'bootstrap.servers': f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}'}
admin_client = AdminClient(client_conf)

consumer_settings = {
        'bootstrap.servers': f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}',
        'enable.auto.commit': True,
        'auto.offset.reset': 'earliest'
}

producer_settings = {'bootstrap.servers': f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}'}

upcreate_consumer = Consumer(
    {**consumer_settings, **{'group.id': settings.UPCREATE_CONSUMER_GROUP_ID, }})
delete_consumer = Consumer(
    {**consumer_settings, **{'group.id': settings.DELETE_CONSUMER_GROUP_ID, }})
producer = Producer(producer_settings)


def message_key():
    return str(int(datetime.now(timezone.utc).timestamp()))


@dataclass
class KafkaThread:
    thread: Thread = None
    thread_stop: bool = True
    consumer: Consumer = None
    function: Any = None

    def start_thread(self):
        if self.thread is None:
            with lock:
                self.thread_stop = False
            self.thread = Thread(
                target=self.function, args=[self, ])
            self.thread.start()

    def stop_thread(self):
        if self.thread is not None:
            with lock:
                self.thread_stop = True
            self.thread.join()
            self.thread = None


def from_kafka_to_db(kafka_thread):
    while True:
        with lock:
            if kafka_thread.thread_stop:
                break
        kafka_thread.consumer.subscribe([settings.UPDATES_TOPIC])
        mess = kafka_thread.consumer.poll(1.0)
        if mess is not None:
            try:
                data = mess.value().decode('utf-8')
                serializer = SomeModelUpCreateSerializer(data=json.loads(data))
                if serializer.is_valid():
                    with lock:
                        serializer.update_or_create()
            except:
                continue    

def kafka_delete(kafka_thread):
    while True:
        with lock:
            if kafka_thread.thread_stop:
                break
        kafka_thread.consumer.subscribe([settings.DELETE_TOPIC])
        mess = kafka_thread.consumer.poll(1.0)
        if mess is not None:
            print(mess)
            try:
                data = mess.value().decode('utf-8')
                print(data)
                id = json.loads(data)['id']
                print(f'mess_id={id}')
                with lock:
                    SomeModel.objects.filter(id=id).delete()
            except:
                continue
    kafka_thread.consumer.commit()


def object_to_kafka(obj):
    serializer = SomeModelSerializer(obj)
    data = json.dumps(serializer.data)
    key = message_key()
    producer.produce(
        settings.OBJECTS_TO_KAFKA_TOPIC, key=key, value=data.encode('utf-8'))
    in_queue = producer.flush()
    response_data = {**serializer.data, 'key': key, 'in_queue': in_queue}
    return response_data


def kill_consumer(consumer):
    consumer_id = consumer.memberid()
    consumer.close()
    admin_client.delete_consumer_groups([consumer_id])


def delete_topics(topic_names):
    fs = admin_client.delete_topics(topic_names, operation_timeout=30)
    for topic, f in fs.items():
        try:
            f.result()
            print("Topic {} deleted".format(topic))
        except Exception as e:
            print("Failed to delete topic {}: {}".format(topic, e))


def create_topics(topic_names):
    topics = [NewTopic(name) for name in topic_names]
    fs = admin_client.create_topics(topics)
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))
