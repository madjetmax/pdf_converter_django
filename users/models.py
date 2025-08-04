from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin

# Create your models here.
class CastomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )
        user.set_password(password)

        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser has to have is_staff being True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser has to have is_superuser being True")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    objects=CastomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = [
    ]
    
    def get_full_name(self):
        return f"{self.first_name.capitalize()} {self.last_name.capitalize()}"
        
    def __str__(self):
        return f"{self.get_full_name()}-{self.pk}"