from django.contrib import admin
# Register your models here.

from .models import Profile
# from buddiaccounts.models import CustomUser


class ProfileAdmin(admin.ModelAdmin):
    fields = ['image_tag', 'birth_date', 'city', 'state', 'zipCode', 'seeker']
    readonly_fields = ['image_tag']
    list_display = ['image_tag']


admin.site.register(Profile, ProfileAdmin)
