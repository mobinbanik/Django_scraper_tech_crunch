from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .views import (
    search_by_keyword_view,
    update_all_categories,
    check
)

urlpatterns = [
    path('', search_by_keyword_view, name='index'),
    path('update/', update_all_categories, name='update'),
    path('check/', check, name='check')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
