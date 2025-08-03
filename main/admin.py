from django.contrib import admin
from .models import Advertisement, PageData, BlogParagraph, TaskAccessToken
from .forms import AdvertisementCreationForm

admin.site.register(PageData)
admin.site.register(BlogParagraph)
admin.site.register(TaskAccessToken)

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    form = AdvertisementCreationForm
