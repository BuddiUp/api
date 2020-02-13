from django.contrib import admin
# Register your models here.

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    fields = ['image_tag', 'user', 'birth_date', 'city', 'state', 'zipCode', 'seeker']
    readonly_fields = ['image_tag']
    list_display = ['user', 'image_tag']


admin.site.register(Profile, ProfileAdmin)
