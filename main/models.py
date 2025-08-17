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
    url_name = models.CharField(max_length=100, blank=False, null=True, unique=True)
    url = models.TextField(unique=True) # endpoint like /example/path/

    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=150, blank=False)
    # like a list of tags separated with \n
    additional_meta_tags = models.TextField(null=True, blank=True)

    h1 = models.CharField(max_length=100, blank=False)
    def get_list_additional_metatags(self) -> list[str]:
        if self.additional_meta_tags:
            return self.additional_meta_tags.split("\n")

        return []
    
    def __str__(self):
        return self.url_name

# for main, blog, questions pages text
class MainPageOtherInfo(models.Model):
    text = models.TextField()

    def __str__(self):
        # return first 30 characters
        return f"{self.text[:30]}... "

class BlogParagraph(models.Model):
    page_data = models.ForeignKey(PageData, on_delete=models.CASCADE)

    title = models.CharField(max_length=255, null=True)
    text = models.TextField(blank=False)
    
    def __str__(self):
        return self.title
    
class QuestionAnswer(models.Model):
    question = models.TextField(blank=False)
    answer = models.TextField(blank=False)

    def __str__(self):
        # return first 20 characters
        return f"{self.question[:20]}... {self.pk}"