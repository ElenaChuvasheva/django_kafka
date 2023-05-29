import json

from confluent_kafka import Producer

for i in range(10):
    p = Producer({'bootstrap.servers': 'localhost:19092'})

    data = {'id': 134, 'name': 'NEW NAME!3333333'}
    delete_data = {'id': 301}

    mess = json.dumps(data)
    delete_mess = json.dumps(delete_data)
    p.produce('updates', value=mess.encode('utf-8'))
    p.produce('deletions', value=delete_mess.encode('utf-8'))
    p.flush()
