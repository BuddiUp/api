from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
#https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
# Link to Articled that explained the process in the Models


def get_image_path(instance, filename):
    print("Triggered, this is the destination:", str(instance.id), filename)
    return os.path.join('photos', str(instance.id), filename)


class Profile(models.Model):
    """ This model Profile will be used to create A profile of the User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=5, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    seeker = models.BooleanField(null=True)
    profile_Image = models.ImageField(upload_to=get_image_path, blank=True, null=True)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
