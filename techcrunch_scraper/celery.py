import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techcrunch_scraper.settings')

app = Celery('techcrunch_scraper', broker=settings.CELERY_BROKER_URL)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'every-60-seconds-scrape-remain-post-search-items': {
        'task': 'techcrunch.tasks.tech_crunch_scrape_remain_post_search_item',
        'schedule': 60,  # In Second
    },
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# celery -A techcrunch_scraper worker -l INFO -P eventlet
# celery -A techcrunch_scraper beat --loglevel=INFO