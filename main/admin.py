from django.contrib import admin
from .models import Advertisement, PageData, BlogParagraph, TaskAccessToken, MainPageOtherInfo
from .forms import AdvertisementCreationForm

admin.site.register(PageData)
admin.site.register(BlogParagraph)
admin.site.register(TaskAccessToken)
admin.site.register(MainPageOtherInfo)

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    form = AdvertisementCreationForm
