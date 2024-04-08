import os

from celery import Celery


# Set the default Django settings module for the 'celery' program.
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'good_reads_scraper_with_django.settings')

app = Celery('good_reads_scraper_with_django', broker=settings.CELERY_BROKER_URL)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'every-60-seconds-scrape-remain-book-search-items': {
        'task': 'goodread.tasks.good_reads_scrape_remain_book_search_item',
        'schedule': 60,  # In Second
    },
    'every-60-seconds-scrape-remain-group-search-items': {
        'task': 'goodread.tasks.good_reads_scrape_remain_group_search_item',
        'schedule': 60,  # In Second
    },
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# celery -A good_reads_scraper_with_django worker -l INFO -P eventlet
# celery -A good_reads_scraper_with_django beat --loglevel=INFO