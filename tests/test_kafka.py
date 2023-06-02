import json

from confluent_kafka import Producer
from django.conf import settings
from django.test import Client, TransactionTestCase
from django.urls import reverse
from freezegun import freeze_time

from api.serializers import SomeModelSerializer
from application.models import SomeModel
from utils.kafka_utils import lock, producer_settings

client = Client()


class KafkaTest(TransactionTestCase):
    def setUp(self):
        with lock:
            SomeModel.objects.create(id=1, name="smth1")

    def tearDown(self):
        with lock:
            SomeModel.objects.all().delete()

    @freeze_time("2012-01-01")
    def test_post_to_kafka(self):
        response = client.post(reverse('api:smth-write-to-kafka', args=['1']))
        assert response.status_code == 200
        with lock:
            item = SomeModel.objects.get(pk=1)
        serializer = SomeModelSerializer(item)
        data = {**serializer.data, 'key': '1325376000', 'in_queue': 0}
        assert response.data == data

    def test_delete_from_kafka(self):
        producer = Producer(producer_settings)
        data = json.dumps({'id': 2})
        with lock:
            SomeModel.objects.create(id=2, name="smth2")
        producer.produce(
            settings.DELETE_TOPIC, value=data.encode('utf-8'))
        producer.flush()
        import time
        response = client.delete(reverse('api:smth-start-delete-from-kafka'))
        time.sleep(5)
        assert response.status_code == 200
        response = client.post(reverse('api:smth-stop-delete-from-kafka'))
        with lock:
            assert SomeModel.objects.count() == 1

    def test_upcreate_from_kafka(self):
        producer = Producer(producer_settings)
        obj_info = {'id': 2, 'name': 'test_name'}
        data = json.dumps(obj_info)
        producer.produce(
            settings.UPDATES_TOPIC, value=data.encode('utf-8'))
        producer.flush()
        import time
        response = client.post(reverse('api:smth-start-upcreate-from-kafka'))        
        time.sleep(5)
        assert response.status_code == 200
        response = client.post(reverse('api:smth-stop-upcreate-from-kafka'))
        with lock:
            assert SomeModel.objects.count() == 2
