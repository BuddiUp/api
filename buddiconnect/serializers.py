
from .models import Profile
from rest_framework import serializers


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'profile_Image', 'bio', 'city', 'state', 'zipCode', 'birth_date', 'seeker']
