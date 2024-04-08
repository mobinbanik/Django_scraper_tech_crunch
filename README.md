# TechCrunch Scraper

TechCrunch Scraper is a Django application designed to extract information from the TechCrunch website, including posts, authors, and categories. It provides functionality to update this data daily in a cron-like manner, ensuring the information is always up-to-date.

## Features

- **Data Extraction**: Scrapes data from the TechCrunch website, including posts, authors, and categories.
- **Scheduled Updates**: Automatically updates the scraped data daily to keep it current.
- **Export Capability**: Utilizes the django-import-export package to provide export functionality for the extracted data.
- **Celery Integration**: Integrated with Celery for task scheduling and background job execution.
- **Sample Settings**: Includes a sample_settings.py file for users to configure their local settings.

## Installation

1. Install the required packages listed in `requirements.txt`:
```pip install -r requirements.txt```
2. Create and configure your `local_settings.py` file based on the provided `sample_settings.py`. This file should contain settings specific to your local environment, such as Celery broker URL and timezone.

3. Migrate the database:
```python manage.py migrate```
4. Create a superuser for accessing the admin panel:
```python manage.py createsuperuser```

## Usage
1. Start the Celery worker:
```celery -A techcrunch worker -l info```

2. Run the Django development server:
```python manage.py runserver```
3.
3. Access the admin panel at `http://localhost:8000/admin` to configure the scheduled updates and manage the scraped data.

## URLs
Use the provided URLs for accessing different functionalities:
- `/`: Display the search page for keyword-based search.
- `/update/`: Trigger the update of all categories.
- `/check/`: Check and update all categories.



The project's URL patterns are defined as follows:

```python
urlpatterns = [
 path('', search_by_keyword_view, name='index'),
 path('update/', update_all_categories, name='update'),
 path('check/', check, name='check')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
# Celery Configuration
The project utilizes Celery for task scheduling and execution. The Celery configuration options are specified in the settings.py file.

```# Celery Configuration Options
CELERY_BROKER_URL = CELERY_LOCAL_BROKER_URL
CELERY_TIMEZONE = CELERY_LOCAL_TIMEZONE
CELERY_TASK_TIME_LIMIT = 60 * 60

CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

# Dependencies
    Django
    django-import-export
    django_celery_beat
    django_celery_results


# GitHub
https://github.com/mobinbanikarim
