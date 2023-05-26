from django.urls import include, path
from rest_framework import routers

from api.views import SomeModelViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('some_models', SomeModelViewSet, basename='smth')

urlpatterns = [
    path('', include(router.urls)),
]
