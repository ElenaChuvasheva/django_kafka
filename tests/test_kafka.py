import json

from confluent_kafka import Producer
from django.conf import settings
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from freezegun import freeze_time
from rest_framework.test import APIClient

from api.serializers import SomeModelSerializer
from application.models import SomeModel
from tests.utils import create_topics, delete_topics
from utils.kafka_utils import lock, producer_settings

client = APIClient()


class KafkaTest(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        pass
        # create_topics([settings.OBJECTS_TO_KAFKA_TOPIC, settings.DELETE_TOPIC])

    
    def setUp(self):
        with lock:
            SomeModel.objects.create(id=1, name="smth1")

    def tearDown(self):
        with lock:
            SomeModel.objects.all().delete()

    @classmethod
    def tearDownClass(cls):
        # в teardown модуля?
        delete_topics(
            [settings.OBJECTS_TO_KAFKA_TOPIC, settings.DELETE_TOPIC, settings.REST_LOG_TOPIC, settings.UPDATES_TOPIC])

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

        # убрать в teardown модуля
        from utils.kafka_utils import delete_consumer
        consumer_id = delete_consumer.memberid()
        delete_consumer.close()        
        from tests.utils import admin_client
        admin_client.delete_consumer_groups([consumer_id])
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

        # убрать в teardown модуля
        from utils.kafka_utils import upcreate_consumer
        consumer_id = upcreate_consumer.memberid()
        upcreate_consumer.close()        
        from tests.utils import admin_client
        admin_client.delete_consumer_groups([consumer_id])
        with lock:
            assert SomeModel.objects.count() == 2
