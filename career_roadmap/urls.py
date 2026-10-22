"""
Root URL file. Django checks this first for every request that comes in,
then hands it off to the correct app based on the prefix.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),          # Django's built-in admin panel
    path('', include('core.urls')),                  # home, dashboard, career, roadmap, etc.
    path('accounts/', include('accounts.urls')),      # login, register, profile, password
]

# While DEBUG=True, this lets Django serve uploaded resumes/profile pics directly
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
