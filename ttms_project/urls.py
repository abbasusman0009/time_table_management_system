from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='accounts:login', permanent=False), name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path('academics/', include('apps.academics.urls')),
    path('venues/', include('apps.venues.urls')),
    path('scheduling/', include('apps.scheduling.urls')),
    path('timetable/', include('apps.timetable.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
