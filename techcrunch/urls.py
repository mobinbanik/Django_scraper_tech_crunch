from django.urls import path

from .views import search_by_keyword_view

urlpatterns = [
    path('', search_by_keyword_view, name='index'),
]
