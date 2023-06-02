from confluent_kafka.admin import AdminClient, NewTopic
from django.conf import settings

client_conf = {'bootstrap.servers': f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}'}
admin_client = AdminClient(client_conf)

def delete_topics(topic_names):        
    fs = admin_client.delete_topics(topic_names, operation_timeout=30)
    for topic, f in fs.items():
        try:
            f.result()
            print("Topic {} deleted".format(topic))
        except Exception as e:
            print("Failed to delete topic {}: {}".format(topic, e))


def create_topics(topic_names):
    topics = [NewTopic(name) for name in topic_names]
    fs = admin_client.create_topics(topics)
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))
    