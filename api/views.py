import json
import time
from threading import Lock, Thread

from confluent_kafka import Consumer, Producer
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import SomeModelSerializer
from application.models import SomeModel

lock = Lock()


class SomeModelViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    queryset = SomeModel.objects.all()
    serializer_class = SomeModelSerializer

    thread_stop = True
    kafka_thread = None
    producer = Producer(
        {'bootstrap.servers':'host.docker.internal:19092'})
    consumer = Consumer(
        {
            'bootstrap.servers':'host.docker.internal:19092',
            'group.id':'pythonconsumer',
            'enable.auto.commit': False,
            'auto.offset.reset': 'latest'
        }
    )

    def list(self, *args, **kwargs):
        with lock:
            return super().list(args, kwargs)

    @staticmethod
    def from_kafka_to_db():
        while not SomeModelViewSet.thread_stop:
            print('mega task process')
            with lock:
                SomeModel.objects.create(name='from thread 3')
            time.sleep(5)

    @action(detail=False, url_path='start_update_from_kafka',
            methods=['POST'])
    def start_update_from_kafka(self, request):
        if SomeModelViewSet.thread_stop:
            SomeModelViewSet.thread_stop = False
            SomeModelViewSet.kafka_thread = Thread(
                target=self.from_kafka_to_db)
            SomeModelViewSet.kafka_thread.start()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, url_path='stop_update_from_kafka',
            methods=['POST'])
    def stop_update_from_kafka(self, request):
        if not SomeModelViewSet.thread_stop:
            SomeModelViewSet.thread_stop = True
            SomeModelViewSet.kafka_thread.join()
            SomeModelViewSet.kafka_thread = None
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
