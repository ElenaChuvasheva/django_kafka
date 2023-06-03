
from typing import Any, List, Tuple
from django.conf import settings
from django.db.backends.base.base import BaseDatabaseWrapper
from django.test.runner import DiscoverRunner
from django.db import connection

from utils.kafka_utils import (delete_consumer, delete_topics, kill_consumer,
                               upcreate_consumer)


class DjangoKafkaRunner(DiscoverRunner):
    def teardown_test_environment(self, **kwargs):
        kill_consumer(delete_consumer)
        kill_consumer(upcreate_consumer)
        delete_topics(
            [settings.OBJECTS_TO_KAFKA_TOPIC, settings.DELETE_TOPIC, settings.REST_LOG_TOPIC, settings.UPDATES_TOPIC])
        return super().teardown_test_environment(**kwargs)
    
    def teardown_databases(self, old_config: List[Tuple[BaseDatabaseWrapper, str, bool]], **kwargs: Any) -> None:        
        cursor = connection.cursor()
        database_name = settings.DATABASES['default']['NAME']
        cursor.execute(
            "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity "
            "WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid();", [database_name])
        return super().teardown_databases(old_config, **kwargs)
