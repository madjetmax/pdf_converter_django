from django.contrib import admin
from .models import Advertisement, PageData, BlogParagraph, TaskAccessToken
# Register your models here.

admin.site.register(Advertisement)
admin.site.register(PageData)
admin.site.register(BlogParagraph)
admin.site.register(TaskAccessToken)

