import json
import time
from dataclasses import dataclass
from threading import Lock, Thread, active_count

from confluent_kafka import Consumer, Producer
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import SomeModelSerializer, SomeModelUpCreateSerializer
from application.models import SomeModel

lock = Lock()


@dataclass
class KafkaThread:
    thread = None
    thread_stop = True

    def start_thread(self, function):
        self.thread_stop = False
        self.thread = Thread(
            target=function)
        self.thread.start()

    def stop_thread(self):
        if not self.thread_stop:
            self.thread_stop = True
            self.thread.join()
            self.thread = None


class SomeModelViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    queryset = SomeModel.objects.all()
    serializer_class = SomeModelSerializer

    upcreate_thread = KafkaThread()
    delete_thread = KafkaThread()

    delete_thread_stop = True
    kafka_delete_thread = None
    producer = Producer(
        {'bootstrap.servers': 'host.docker.internal:19092'})
    consumer_settings = {
            'bootstrap.servers': 'host.docker.internal:19092',
            'group.id': 'pythonupcreate_consumer',
            'enable.auto.commit': True,
            'auto.offset.reset': 'earliest'
    }
    upcreate_consumer = Consumer(consumer_settings)
    delete_consumer = Consumer(consumer_settings)

    def list(self, *args, **kwargs):
        with lock:
            return super().list(args, kwargs)

    def from_kafka_to_db(self):
        while not SomeModelViewSet.upcreate_thread.thread_stop:
            print('mega task process')
            self.upcreate_consumer.subscribe(['updates'])
            mess = self.upcreate_consumer.poll(1.0)
            if mess is not None:
                data = mess.value().decode('utf-8')
                serializer = SomeModelUpCreateSerializer(data=json.loads(data))
                print('updating...')
                if serializer.is_valid():
                    with lock:                        
                        serializer.update_or_create()
                        print('!!!!!!!!!!UPDATED!!!!!!!!!!!')

    def kafka_delete(self):
        while not SomeModelViewSet.delete_thread.thread_stop:
            print('delete thread')
            self.delete_consumer.subscribe(['deletions'])
            mess = self.delete_consumer.poll(1.0)
            print(mess)
            if mess is not None:
                data = mess.value().decode('utf-8')
                id = json.loads(data)['id']
                print('deleting...')
                with lock:
                    SomeModel.objects.filter(id=id).delete()
                    print('!!!!!!!!!!DELETED!!!!!!!!!!!')

    @action(detail=False, url_path='start_upcreate_from_kafka',
            methods=['POST'])
    def start_upcreate_from_kafka(self, request):
        SomeModelViewSet.upcreate_thread.start_thread(self.from_kafka_to_db)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, url_path='stop_upcreate_from_kafka',
            methods=['POST'])
    def stop_upcreate_from_kafka(self, request):
        SomeModelViewSet.upcreate_thread.stop_thread()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, url_path='start_delete_from_kafka',
            methods=['DELETE'])
    def start_delete_from_kafka(self, request):
        SomeModelViewSet.delete_thread.start_thread(self.kafka_delete)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, url_path='stop_delete_from_kafka',
            methods=['POST'])
    def stop_delete_from_kafka(self, request):
        SomeModelViewSet.delete_thread.stop_thread()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, url_path='write_to_kafka',
            methods=['POST'])
    def write_to_kafka(self, request, pk):
        with lock:
            obj = get_object_or_404(SomeModel, id=pk)
        serializer = SomeModelSerializer(obj)
        data = json.dumps(serializer.data)
        self.producer.produce('some_model_objects', value=data.encode('utf-8'))
        self.producer.flush()
        return Response(serializer.data, status=status.HTTP_200_OK)
