from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django import forms
from .models import Advertisement, PageData, BlogParagraph
from django.utils.translation import gettext_lazy as _

import os

def file_size_validator(value):
    size_limit_mb = 20
    limit = size_limit_mb * 1024 * 1024
    if value.size > limit:
        raise ValidationError(
            _("File is too big, max allowed size is {size_limit_mb} MB").format(size_limit_mb=size_limit_mb),
        )

class FileUploadForm(forms.Form):
    file = forms.FileField(
        validators=[FileExtensionValidator(["pdf"], message=_("Invalid file extension.\nAllowed extensions are: pdf")), file_size_validator],
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf'}),
    )  

# * for admin
class PageDataCreationForm(forms.ModelForm):
    class Meta:
        model = PageData
        fields = "__all__"

        widgets = {
            "url": forms.TextInput(attrs={"class": "vTextField"}),  # render as <input type="text">
        }


class AdvertisementCreationForm(forms.ModelForm):
    content_file = forms.FileField(
        label="Image, GIF, Video",
        validators=[FileExtensionValidator(allowed_extensions=('gif', 'jpg', 'jpeg', 'png', "mp4"))]
    )
    class Meta:
        model = Advertisement
        fields = [
            "content_file",
            "image_url",
            "url",
            "date_created",
        ]
    @staticmethod
    def get_content_type(model: Advertisement) -> tuple[str, str | None] | tuple[None, None]:
        
        # get extention
        ext = os.path.splitext(model.content_file.name)[1].lower()  # get file extension with dot
        ext = ext.lstrip('.')  # remove dot

        # return content type
        if ext in ['jpg', 'jpeg', 'png', 'bmp', 'webp']:
            return 'image', None
        elif ext in ['gif']:
            return 'gif', None
        elif ext in ['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv']:
            return 'video', ext

        return None, None

    # to set content_type and video_type
    def save(self, commit = ...):
        model: Advertisement =  super().save(commit)
        # get and set content type for file
        content_type, ext = self.get_content_type(model)
        model.content_type = content_type

        # set video type
        if content_type == "video":
            model.video_type = ext

        model.save()
        return model