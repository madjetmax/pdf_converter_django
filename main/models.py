from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.files.base import ContentFile
from django.utils import timezone
from uuid import uuid4

class TaskAccessToken(models.Model):
    task_id = models.CharField(max_length=255, unique=True)
    access_token = models.UUIDField(default=uuid4, unique=True)    


def create_unique_image_path(instanse, filename: str):
    directory = "ads_images"
    extention = ".".join(filename.split(".")[1:])
    file_path = f"{directory}/{uuid4()}.{extention}"
    return file_path

class Advertisement(models.Model):
    content_file = models.FileField(
        null=True, blank=True, 
        upload_to=create_unique_image_path,
        validators=[FileExtensionValidator(allowed_extensions=('gif', 'jpg', 'jpeg', 'png', "mp4"))]
    )
    image_url = models.URLField(null=True, blank=True)

    url = models.URLField()

    # other
    content_type = models.CharField(max_length=50, null=True, blank=True)
    video_type = models.CharField(max_length=50, null=True, blank=True)

    # date 
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    

class PageData(models.Model):
    url_name = models.CharField(max_length=100, blank=False, null=True)
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=150, blank=False)
    h1 = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return self.url_name


class BlogParagraph(models.Model):
    text = models.TextField(blank=False)
    
    show_more_button = models.BooleanField(default=True, blank=False)
    max_text_rows = models.IntegerField(default=3, validators=[MinValueValidator(1)], blank=False)

    def __str__(self):
        # return first 20 characters
        return f"{self.text[:20]}... {self.pk}"
    
class MainPageOtherInfo(models.Model):
    text = models.TextField()

    def __str__(self):
        # return first 30 characters
        return f"{self.text[:30]}... "