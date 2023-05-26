from rest_framework import viewsets

from api.serializers import SomeModelSerializer
from application.models import SomeModel


class SomeModelViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete')

    queryset = SomeModel.objects.all()
    serializer_class = SomeModelSerializer
