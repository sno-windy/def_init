from django.contrib.sitemaps import Sitemap
from .models import *


class IndexSitemap(Sitemap):
    def items(self):
        return ['top']

    def location(self,obj):
        return '/'
