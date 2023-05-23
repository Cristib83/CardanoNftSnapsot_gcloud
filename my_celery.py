import os
import logging
from celery import Celery
from urllib.parse import urlparse
import redis


url = urlparse(os.environ.get('REDIS_URL'))
broker_url = f"redis://{url.hostname}:{url.port}/{url.path[1:]}"
result_backend = f"redis://{url.hostname}:{url.port}/{url.path[1:]}"


# Get Redis URL from environment variable, or use default URL
redis_url =os.environ.get('REDIS_URL')
r = redis.from_url(redis_url)
# Create a Celery instance named 'tasks' with Redis as the broker
celery_app = Celery('tasks', broker=redis_url, backend=redis_url)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
