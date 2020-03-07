from django.db import models
from buddiaccounts.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
import pathlib
import os
from django.utils.html import mark_safe
from PIL import Image
import PIL
from io import BytesIO
from django.core.files import File

#https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
# Link to Articled that explained the process in the Models


def get_image_path(instance, filename):
    print("Triggered, this is the destination:", str(instance.id), filename)
    return os.path.join('photos', str(instance.id), filename)


def default_image_path():
    im = Image.open(r"static/default_Images/photos/default-image.png", mode='r')
    sizeb = os.path.getsize('static/default_Images/photos/default-image.png')
    print("Size in bytes", sizeb)
    thumb_io = BytesIO(sizeb.to_bytes(10, 'big')) # create a BytesIO object
    im = im.resize((400, 400), PIL.Image.ANTIALIAS)
    im.save(thumb_io, 'PNG', quality=90) # save image to BytesIO object
    thumbnail = File(thumb_io, name='default-image.png') # create a django friendly File object
    return thumbnail


class Profile(models.Model):
    """ This model Profile will be used to create A profile of the User"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    profile_Image = models.ImageField(upload_to=get_image_path, blank=True, null=True)  #default=os.path.join('default_Images/photos/default-image.png'))
    name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zipcode = models.IntegerField(null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    birth_month = models.CharField(max_length=2,  blank=True)
    birth_day = models.CharField(max_length=2,  blank=True)
    birth_year = models.CharField(max_length=4, blank=True)
    age = models.CharField(max_length=3, blank=True)
    seeker = models.BooleanField(default=True, blank=True)
    password = models.CharField(max_length=100, blank=True)
    profile_urlfield = models.URLField(max_length=200)
    user_uuid = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.email

    def image_tag(self):
        try:
            return mark_safe('<img src="/photos/%s" width="150" height="150" />' % (self.profile_Image))
        except Exception:
            pass


@receiver(post_save, sender=CustomUser)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
