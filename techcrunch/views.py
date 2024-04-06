from django.shortcuts import render

from .forms import SearchByKeywordForm
from .models import Keyword, SearchedKeyword
from .scraper_handler import ScraperHandler


# Create your views here.
def search_by_keyword_view(request):
    if request.method == 'POST':
        form = SearchByKeywordForm(request.POST)
        if form.is_valid():
            # TODO: '+'.join(cleaned_data['keyword'].split(' '))
            data = {
                'keyword': form.cleaned_data['keyword'],
                'page_count': form.cleaned_data['page_count'],
            }

            keyword, _ = Keyword.objects.get_or_create(
                title=form.cleaned_data['keyword'],
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