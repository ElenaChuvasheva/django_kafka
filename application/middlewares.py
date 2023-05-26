import json

import rest_framework
from confluent_kafka import Producer


def make_kafka_data(request, response):
    return {
        'url': request.path,
        'request_method': request.method,
        'status': response.status_code,
        'data': response.data if hasattr(response, 'data') else None
    }


def kafka_save_response_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        if isinstance(response, rest_framework.response.Response):
            producer = Producer(
                {'bootstrap.servers': 'host.docker.internal:19092'})
            result_json = json.dumps(make_kafka_data(request, response))
            producer.produce('django-responses', value=result_json.encode('utf-8'))
            producer.flush()
        return response
    return middleware
