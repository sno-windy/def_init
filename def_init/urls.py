from django.contrib import admin
from django.urls import path,include
import def_i.views as def_i #いる？
from django.contrib.staticfiles.urls import static,staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('def_i.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
