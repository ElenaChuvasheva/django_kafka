import json
from dataclasses import dataclass
from threading import Lock, Thread

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

upcreate_consumer = Consumer(
    {**consumer_settings, **{'group.id': 'pythonupcreate_consumer', }})
delete_consumer = Consumer(
    {**consumer_settings, **{'group.id': 'pythondelete_consumer', }})
producer = Producer(
    {'bootstrap.servers': f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}'})


@dataclass
class KafkaThread:
    thread = None
    thread_stop = True
    consumer = None

    def start_thread(self, consumer, function):
        self.thread_stop = False
        self.consumer = consumer
        self.thread = Thread(
            target=function, args=[self, ])
        self.thread.start()

    def stop_thread(self):
        if not self.thread_stop:
            self.thread_stop = True
            self.thread.join()
            self.thread = None
            self.consumer = None


def from_kafka_to_db(kafka_thread):
    while not kafka_thread.thread_stop:
        print('update thread')
        kafka_thread.consumer.subscribe([settings.UPDATES_TOPIC])
        mess = kafka_thread.consumer.poll(1.0)
        if mess is not None:
            try:
                data = mess.value().decode('utf-8')
                serializer = SomeModelUpCreateSerializer(data=json.loads(data))
                print('updating...')
                if serializer.is_valid():
                    print(lock)
                    with lock:
                        serializer.update_or_create()
                        print('!!!!!!!!!!UPDATED!!!!!!!!!!!')
            except (json.decoder.JSONDecodeError, AttributeError):
                continue


def kafka_delete(kafka_thread):
    while not kafka_thread.thread_stop:
        print('delete thread')
        kafka_thread.consumer.subscribe([settings.DELETE_TOPIC])
        mess = kafka_thread.consumer.poll(1.0)
        print(mess)
        if mess is not None:
            try:
                data = mess.value().decode('utf-8')
                print(data)
                id = json.loads(data)['id']
                print('deleting...')
                with lock:
                    SomeModel.objects.filter(id=id).delete()
                    print('!!!!!!!!!!DELETED!!!!!!!!!!!')
            except (json.decoder.JSONDecodeError, AttributeError):
                continue


def object_to_kafka(obj):
    serializer = SomeModelSerializer(obj)
    data = json.dumps(serializer.data)
    producer.produce(
        settings.OBJECTS_TO_KAFKA_TOPIC, value=data.encode('utf-8'))
    producer.flush()
    return serializer.data
