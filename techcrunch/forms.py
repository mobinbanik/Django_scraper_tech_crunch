from django import forms
from django.conf import settings


class SearchByKeywordForm(forms.Form):

    keyword = forms.CharField(label='Keyword', max_length=255)
    page_count = forms.IntegerField(
        label='Page Count',
        initial=settings.GOOD_READS_DEFAULT_SEARCH_PAGE_COUNT,
        min_value=1,
        max_value=settings.GOOD_READS_MAXIMUM_SEARCH_PAGE_COUNT,
    )
