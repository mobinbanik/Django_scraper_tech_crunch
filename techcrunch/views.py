from django.shortcuts import render, HttpResponse

from .forms import SearchByKeywordForm, CategoryUpdateForm
from .models import Keyword, SearchedKeyword
from .scraper_handler import ScraperHandler
from django.conf import settings


# Create your views here.
def search_by_keyword_view(request):
    if request.method == 'POST':
        form = SearchByKeywordForm(request.POST)
        if form.is_valid():
            keyword_text = '+'.join(form.cleaned_data['keyword'].split(' '))

            keyword, _ = Keyword.objects.get_or_create(
                title=keyword_text,
            )
            search_by_keyword_instance = SearchedKeyword.objects.create(
                keyword=keyword,
                page_count=form.cleaned_data['page_count']
            )

            scraper_handler = ScraperHandler()

            scraper_handler.search_by_keyword(search_by_keyword_instance)

            return render(request, 'techcrunch/search.html', {'form': form})

    else:
        form = SearchByKeywordForm()

    return render(request, 'techcrunch/search.html', {'form': form})


def update_all_categories(request):
    if request.method == 'POST':
        form = CategoryUpdateForm(request.POST)
        if form.is_valid():
            scraper_handler = ScraperHandler()
            scraper_handler.create_or_update_category_list(settings.DEFAULT_CATEGORY_COUNT_UPDATE)
            return render(request, 'techcrunch/update.html', {'form': form})
    else:
        form = CategoryUpdateForm()
    return render(request, 'techcrunch/update.html', {'form': form})


def check(request):
    if request.method == 'GET':
        scraper_handler = ScraperHandler()
        scraper_handler.update_posts_for_all_categories()
        return HttpResponse('done!')
