# django_kafka
Используется Python 3.10.
## Запуск

Клонируйте репозиторий:
```
git clone git@github.com:ElenaChuvasheva/django_kafka.git
```
Перейдите в папку django_kafka:
```
cd django_kafka
```
Создайте в этой папке файл .env. Пример содержания файла:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=host.docker.internal
DB_PORT=5432
KAFKA_HOST=host.docker.internal
KAFKA_PORT=19092
UPDATES_TOPIC=updates
DELETE_TOPIC=deletions
OBJECTS_TO_KAFKA_TOPIC=some_model_objects
REST_LOG_TOPIC=django-responses
SECRET_KEY=django-insecure-8qy4qg1seks68+#4w1-2h$+6v68fb@!vck(+m8_3-w%eq2uee&
```
Запустите команду сборки контейнеров с очередью и базой данных:
```
docker-compose up
```
Примените миграции базы данных:
```
docker-compose exec web python manage.py migrate
```
Интерфейс очереди запустится по адресу localhost:14080, сервер - по адресу localhost:8000.
Запуск тестов:
```
docker-compose exec web python manage.py test
```

## Эндпоинты
  
**GET /api/some_models/** - вывод данных обо всех объектах.  
  
**POST /api/some_models/start_upcreate_from_kafka/** - начать считывать данные из топика очереди *upgrade* и записывать в базу. Формат данных: {"id": 5, "name": "smth"}. Если объект с таким id уже существует, его данные перезаписываются, если не существует, создаётся.
  
**POST /api/some_models/stop_upcreate_from_kafka/** - прекратить считывать данные из очереди.  
  
**DELETE /api/some_models/start_delete_from_kafka/** - начинаем считывать из топика очереди *deletions* сообщения в формате {"id": 1} и удалять соответствующие объекты.  
  
**POST /api/some_models/stop_delete_from_kafka/** - прекращаем считывать из очереди сообщения в формате {"id": 1} и удалять соответствующие объекты.  
  
**POST /api/some_models/2/write_to_kafka/** - запись данных одного объекта в топик очереди *some_model_objects* в формате {"id": 5, "name": "smth"}.
  
  
Также ответы REST записываются в топик *django_responses* с помощью middleware.
