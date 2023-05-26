import time
from threading import Thread, active_count

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import SomeModelSerializer
from application.models import SomeModel


class SomeModelViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    queryset = SomeModel.objects.all()
    serializer_class = SomeModelSerializer
    
    thread_stop = True

    def go(self):
        while not SomeModelViewSet.thread_stop:
            print('mega task process')
            time.sleep(5)

    @action(detail=False, url_path='start_update_from_kafka', methods=['POST'])
    def start_update_from_kafka(self, request):
        if SomeModelViewSet.thread_stop:
            SomeModelViewSet.thread_stop = False
            t = Thread(target=self.go)
            print(active_count())
            t.start()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='stop_update_from_kafka', methods=['POST'])
    def stop_update_from_kafka(self, request):
        SomeModelViewSet.thread_stop = True
        return Response(status=status.HTTP_204_NO_CONTENT)
