"""
URLs principales de Horarium.

Cada app mantiene sus rutas propias y aqui solo se monta el prefijo general:
auth, users, schedules, absences, reports y admin.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls.auth_urls')),
    path('api/users/', include('apps.users.urls.user_urls')),
    path('api/schedules/', include('apps.schedules.urls')),
    path('api/absences/', include('apps.absences.urls')),
    path('api/reports/', include('apps.reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
