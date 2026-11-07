from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hotels.urls')),

    # Temporary media serving for the StayLux portfolio demo
    re_path(
        r'^media/(?P<path>.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]