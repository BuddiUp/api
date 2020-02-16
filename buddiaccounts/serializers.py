from rest_framework import serializers
from django.contrib.auth.models import User
from buddiconnect.models import Profile
from buddiconnect.forms import validate_image
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    '''User Serializer'''
    class Meta:
        model = User
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    '''User Serializer'''
    class Meta:
        model = Profile
        fields = "__all__"


class RegisterSerializer(serializers.ModelSerializer):
    '''Register Serializer'''
    class Meta:
        model = Profile
        fields = ('profile_Image', 'bio', 'city', 'state', 'zipCode', 'email', 'birth_date', 'seeker', 'password', 'username')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # load the profile instance created by the signal
        # validated_data handles hashing of the password
        User.objects.create_user(
              validated_data['username'], validated_data['email'], validated_data['password'])
        # form = SignUpForm(self, instance=user)
        username = validated_data['username']
        user_profile = User.objects.get(username=username)
        user_profile.refresh_from_db()
        user_profile.profile.profile_Image = validate_image(validated_data['profile_Image'])
        user_profile.profile.email = validated_data['email']
        user_profile.profile.bio = validated_data['bio']
        user_profile.profile.city = validated_data['city']
        user_profile.profile.state = validated_data['state']
        user_profile.profile.zipCode = validated_data['zipCode']
        user_profile.profile.birth_date = validated_data['birth_date']
        user_profile.profile.seeker = validated_data['seeker']
        user_profile.profile.save()
        user = User.objects.get(id=user_profile.profile.id)
        return user


class LoginSerializer(serializers.Serializer):
    '''Login Serializer'''
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)

        if user and user.is_active:
            """  If authentication passed, user will be active, else Auth must have failed"""
            return user
        else:
            raise serializers.ValidationError("Incorrect Credentials")
