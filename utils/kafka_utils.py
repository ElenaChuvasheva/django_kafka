import json
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock, Thread, active_count
from typing import Any, Callable

from confluent_kafka import Consumer, Producer
from django.conf import settings

from api.serializers import SomeModelSerializer, SomeModelUpCreateSerializer
from application.models import SomeModel

lock = Lock()

consumer_settings = {
        'bootstrap.servers': f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}',
        'enable.auto.commit': True,
        'auto.offset.reset': 'earliest'
}

producer_settings = {'bootstrap.servers': f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}'}

upcreate_consumer = Consumer(
    {**consumer_settings, **{'group.id': 'pythonupcreate_consumer', }})
delete_consumer = Consumer(
    {**consumer_settings, **{'group.id': 'pythondelete_consumer', }})
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
            try:
                data = mess.value().decode('utf-8')
                id = json.loads(data)['id']
                with lock:
                    SomeModel.objects.filter(id=id).delete()
            except:
                continue


def object_to_kafka(obj):
    serializer = SomeModelSerializer(obj)
    data = json.dumps(serializer.data)
    producer.produce(
        settings.OBJECTS_TO_KAFKA_TOPIC, key=message_key(), value=data.encode('utf-8'))
    producer.flush()
    return serializer.data
