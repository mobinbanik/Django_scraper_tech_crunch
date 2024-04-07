from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .views import search_by_keyword_view

urlpatterns = [
    path('', search_by_keyword_view, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
