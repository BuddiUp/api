from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from django.utils.html import mark_safe

#https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
# Link to Articled that explained the process in the Models


def get_image_path(instance, filename):
    print("Triggered, this is the destination:", str(instance.id), filename)
    return os.path.join('photos', str(instance.id), filename)


class Profile(models.Model):
    """ This model Profile will be used to create A profile of the User"""
    profile_Image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zipCode = models.CharField(max_length=5, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    seeker = models.BooleanField(null=True)
    password = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.user.username

    def image_tag(self):
        return mark_safe('<img src="/photos/%s" width="150" height="150" />' % (self.profile_Image))


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
