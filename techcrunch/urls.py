from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .views import (
    search_by_keyword_view,
    update_all_categories,
    check,
    plot_view,
)

urlpatterns = [
    path('', search_by_keyword_view, name='search'),
    path('update/', update_all_categories, name='update'),
    path('check/', check, name='check'),
    path('plot/', plot_view, name='plot'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
