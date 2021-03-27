from django.contrib import admin
from django.urls import path,include
import def_i.views as def_i #いる？
from django.contrib.staticfiles.urls import static,staticfiles_urlpatterns
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('def_i.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
