from django.test import TransactionTestCase
from django.test.client import Client
from django.urls import reverse

from api.serializers import SomeModelSerializer
from application.models import SomeModel
from utils.kafka_utils import lock

client = Client()


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
        with lock:
            SomeModel.objects.all().delete()

    def test_get_all_items(self):
        response = client.get(reverse('api:smth-list'))
        with lock:
            items = SomeModel.objects.all()
        serializer = SomeModelSerializer(items, many=True)
        self.assertEqual(response.data, serializer.data)
