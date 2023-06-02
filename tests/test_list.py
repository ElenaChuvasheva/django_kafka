from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient

from api.serializers import SomeModelSerializer
from application.models import SomeModel
from tests.utils import delete_topics
from utils.kafka_utils import lock
from django.test.client import Client

client = APIClient()


class GetAllItemsTest(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        bulk = [
            SomeModel(id=1, name="aaa"),
            SomeModel(id=2, name="bbb"),
            SomeModel(id=3, name="ccc")
        ]
        with lock:
            SomeModel.objects.bulk_create(bulk)

    @classmethod
    def tearDownClass(cls):
        # в teardown модуля?
        delete_topics(
            [settings.REST_LOG_TOPIC])

    @classmethod
    def tearDownClass(cls):
        with lock:
            SomeModel.objects.all().delete()

    def test_get_all_items(self):
        response = client.get(reverse('api:smth-list'))
        with lock:
            items = SomeModel.objects.all()
        serializer = SomeModelSerializer(items, many=True)
        self.assertEqual(response.data, serializer.data)
