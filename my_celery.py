import os
import logging
from celery import Celery

# Get Redis URL from environment variable, or use default URL
redis_url = os.environ.get('REDIS_URL')
# Create a Celery instance named 'tasks' with Redis as the broker
celery_app = Celery('tasks', broker=redis_url)

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')