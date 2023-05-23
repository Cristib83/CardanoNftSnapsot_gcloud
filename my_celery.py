import os
import logging
from celery import Celery
import redis


redis_url = os.environ.get('REDIS_URL')
r = redis.from_url(redis_url)

# Create a Celery instance named 'tasks' with Redis as the broker and result backend
celery_app = Celery('tasks', broker=redis_url, backend=redis_url)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
