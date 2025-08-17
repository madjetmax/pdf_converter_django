from django.contrib import admin
from .models import (
    Advertisement, 
    PageData, 
    TaskAccessToken, 
    BlogParagraph, 
    MainPageOtherInfo,
    QuestionAnswer
)
from .forms import (
    AdvertisementCreationForm, 
    PageDataCreationForm,
)

# register 
admin.site.register(TaskAccessToken)
admin.site.register(MainPageOtherInfo)
admin.site.register(QuestionAnswer)
admin.site.register(BlogParagraph)

# register with classes
@admin.register(PageData)
class PageDataAdmin(admin.ModelAdmin):
    form = PageDataCreationForm
    list_display = ("url_name", "url")
    inlines = []

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    form = AdvertisementCreationForm
