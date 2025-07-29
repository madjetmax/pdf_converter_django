from django.contrib import admin
from .models import User
# Register your models here.


# admin.site.register(User)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "id", "date_joined")
    list_filter = ('date_joined',)
    search_fields = ('email', "first_name", "last_name", "id")