from django.contrib import admin
from .models import (
    Advertisement, 
    PageData, 
    TaskAccessToken, 
    BlogParagraph, 
    MainPageOtherInfo,
    QuestionAnswer
)
from .forms import AdvertisementCreationForm

admin.site.register(PageData)
admin.site.register(TaskAccessToken)

admin.site.register(BlogParagraph)
admin.site.register(MainPageOtherInfo)
admin.site.register(QuestionAnswer)

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    form = AdvertisementCreationForm
