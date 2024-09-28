from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from short_url import decode_url

from api.views import RecipeViewSet


def recipe_from_short_url(request, short_url):
    pk = decode_url(short_url)
    return RecipeViewSet.as_view({'get': 'retrieve'})(request, pk=pk)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('s/<str:short_url>/', recipe_from_short_url),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
