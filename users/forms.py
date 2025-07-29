from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.utils.translation import gettext_lazy as _

# from django.contrib.auth.models import  User
from .models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=100,
        required=True,
    )
    first_name = forms.CharField(
        label=_("First Name"),
        max_length=100,
        required=True,
    )
    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=100,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # clear hepl texts 
        for field in self.fields.values():
            field.help_text = None

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            # get and delete user with not active account
            user = User.objects.get(email=email)
            if not user.is_active:
                user.delete()
                return email
            
            # user exists and acount is active
            raise forms.ValidationError(_("Email already exists")) 
        except User.DoesNotExist:            
            return email
        
    class Meta:
        model = User
        fields = [
            "email", 
            "first_name",
            "last_name",
            "password1", 
            "password2"
        ]

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        max_length=100,
        widget=forms.EmailInput(attrs={
            "name": "email",       # custom HTML name attribute
            "class": "form-control",  # your desired CSS class
        })
    )

    # check email
    def clean_username(self):
        email = self.cleaned_data["username"]
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                self.add_error(
                    None, forms.ValidationError(_("Activate Your Account to Sign In!")) 
                )
                return None
            return email
        except User.DoesNotExist:            
            return email
        
    class Meta:
        model = User
        fields = [
            "username", 
            "password"
        ]
