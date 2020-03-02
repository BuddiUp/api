from django.contrib import admin
# Register your models here.
from django.utils.html import format_html
from .models import Profile
# from django.utils.safestring import mark_safe
# from buddiaccounts.models import CustomUser


class ProfileAdmin(admin.ModelAdmin):
    fields = ['image_tag', 'age', 'city', 'state', 'zipcode', 'seeker']
    readonly_fields = ['image_tag']
    list_display = ['age', 'image_tag']

    
admin.site.register(Profile, ProfileAdmin)
