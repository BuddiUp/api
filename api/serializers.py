from buddiaccounts.models import CustomUser
from buddiconnect.models import Profile
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'profile_Image', 'bio', 'city', 'state', 'zipCode', 'birth_date', 'seeker']

#
# class GroupSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Group
#         fields = ['url', 'name']
