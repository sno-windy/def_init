from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'date_joined', 'position','like_count')

admin.site.register(User,UserAdmin)
