from django.shortcuts import render, HttpResponse
from django.conf import settings

from .forms import SearchByKeywordForm, CategoryUpdateForm
from .tasks import (
    tech_crunch_search_by_keyword_task,
    tech_crunch_create_or_update_all_categories,
    tech_crunch_update_posts_for_all_categories,
)
from .scraper_handler import ScraperHandler
from .models import Keyword, SearchedKeyword


# Create your views here.
def search_by_keyword_view(request):
    if request.method == 'POST':
        form = SearchByKeywordForm(request.POST)
        if form.is_valid():
            keyword_text = '+'.join(form.cleaned_data['keyword'].split(' '))
            page_count = form.cleaned_data['page_count']

            # TODO: Without Celery
            # keyword, _ = Keyword.objects.get_or_create(
            #     title=keyword_text,
            # )
            # search_by_keyword_instance = SearchedKeyword.objects.create(
            #     keyword=keyword,
            #     page_count=page_count,
            # )
            #
            # scraper_handler = ScraperHandler()
            #
            # scraped_item_count = len(
            #     scraper_handler.search_by_keyword(search_by_keyword_instance)
            # )

            # TODO: With Celery
            tech_crunch_search_by_keyword_task.delay(
                keyword=keyword_text,
                page_count=page_count,
            )

            return render(request, 'techcrunch/search.html', {'form': form})

    else:
        form = SearchByKeywordForm()

    return render(request, 'techcrunch/search.html', {'form': form})


def update_all_categories(request):
    if request.method == 'POST':
        form = CategoryUpdateForm(request.POST)
        if form.is_valid():
            # TODO: Without Celery
            # scraper_handler = ScraperHandler()
            # scraper_handler.create_or_update_category_list(settings.DEFAULT_CATEGORY_COUNT_UPDATE)
            # TODO: With Celery
            tech_crunch_create_or_update_all_categories.delay()
            return render(request, 'techcrunch/update.html', {'form': form})
    else:
        form = CategoryUpdateForm()
    return render(request, 'techcrunch/update.html', {'form': form})


def check(request):
    if request.method == 'GET':
        # TODO: Without Celery
        # scraper_handler = ScraperHandler()
        # scraper_handler.update_posts_for_all_categories()

        # TODO: With Celery
        tech_crunch_update_posts_for_all_categories.delay()

        return HttpResponse('done!')
