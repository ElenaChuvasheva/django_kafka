from threading import active_count

from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import SomeModelSerializer
from application.models import SomeModel
from utils.kafka_utils import (KafkaThread, delete_consumer, from_kafka_to_db,
                               kafka_delete, lock, object_to_kafka,
                               upcreate_consumer)


class SomeModelViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    queryset = SomeModel.objects.all()
    serializer_class = SomeModelSerializer

    upcreate_thread = KafkaThread(consumer=upcreate_consumer,
                                  function=from_kafka_to_db)
    delete_thread = KafkaThread(consumer=delete_consumer,
                                function=kafka_delete)

    def list(self, *args, **kwargs):
        with lock:
            return super().list(args, kwargs)

    @action(detail=False, url_path='start_upcreate_from_kafka',
            methods=['POST'])
    def start_upcreate_from_kafka(self, request):
        SomeModelViewSet.upcreate_thread.start_thread()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, url_path='stop_upcreate_from_kafka',
            methods=['POST'])
    def stop_upcreate_from_kafka(self, request):
        SomeModelViewSet.upcreate_thread.stop_thread()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, url_path='start_delete_from_kafka',
            methods=['DELETE'])
    def start_delete_from_kafka(self, request):
        SomeModelViewSet.delete_thread.start_thread()
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
        response_data = object_to_kafka(obj)
        return Response(response_data, status=status.HTTP_200_OK)
