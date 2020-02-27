from django.contrib.auth.hashers import check_password
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .managers import CustomUserManager
import uuid
import base64


class EmailBackend(object):
    def authenticate(self, email="", password=""):
        try:
            user = CustomUser.objects.get(email=email)
            if check_password(password, user.password):
                return user
            else:
                return None
        except CustomUser.DoesNotExist:

            # No user was found, return None - triggers default login failed
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    userid = models.CharField(max_length=100, blank=True, unique=True, null=True, default=base64.urlsafe_b64encode(uuid.uuid1().bytes).rstrip(b'=').decode('ascii'))
    date_joined = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
