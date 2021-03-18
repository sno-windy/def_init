from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Article, Question, Like, Clear, Talk

admin.site.register(User, UserAdmin)
admin.site.register(Article)
admin.site.register(Question)
admin.site.register(Like)
admin.site.register(Clear)
admin.site.register(Talk)