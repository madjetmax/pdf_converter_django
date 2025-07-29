from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django import forms
from django.utils.translation import gettext_lazy as _

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