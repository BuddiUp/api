from rest_framework import serializers
from buddiconnect.models import Profile
from buddiconnect.forms import validate_image, compareImages
from .models import EmailBackend, CustomUser
from os import path
import pygame


class UserSerializer(serializers.ModelSerializer):
    '''User Serializer'''
    class Meta:
        model = CustomUser
        fields = "__all__"


class UserSearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    '''User Serializer'''
    class Meta:
        model = Profile
        fields = ('bio', 'city', 'state', 'zipCode', 'birth_date', 'seeker', 'profile_Image')

        def create(self, validated_data):
            """ Validate that the user is Connected"""
            user = CustomUser.objects.get(email=self.request.user.email)
            image_Comparison = compareImages(user.profile.profile_Image, validate_image(validated_data['profile_Image']))
            if user.bio != validated_data['bio']:
                user.profile.bio = validated_data['bio']
            if user.bio != validated_data['city']:
                user.profile.city = validated_data['city']
            if user.state != validated_data['state']:
                user.profile.state = validated_data['state']
            if user.zipCode != validated_data['zipCode']:
                user.profile.zipCode = validated_data['zipCode']
            if user.birth_date != validated_data['birth_date']:
                user.profile.birth_date = validated_data['birth_date']
            if user.seeker != validated_data['seeker']:
                user.profile.seeker = validated_data['seeker']
            if image_Comparison is False:
                user.profile.profile_Image = validate_image(validated_data['profile_Image'])


class RegisterSerializer(serializers.ModelSerializer):
    '''Register Serializer'''
    class Meta:
        model = CustomUser
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # load the profile instance created by the signal
        # validated_data handles hashing of the password
        user = CustomUser.objects.create_user(
             validated_data['email'], validated_data['password'])
        # user_profile = CustomUser.objects.get(email=validated_data['email'])
        user.refresh_from_db()
        # image = pygame.image.load(path.join('api/default_Images/photos', 'default-image.png'))
        # user.profile.profile_Image = pygame.display(image)
        # print("Image", user.profile.profile_Image)

        user.profile.save()
        return user


class LoginSerializer(serializers.Serializer):
    '''Login Serializer'''
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = EmailBackend.authenticate(self, **data)
        print("This is the self parameter", self)
        if user and user.is_active:
            """  If authentication passed, user will be active, else Auth must have failed"""
            return user
        else:
            raise serializers.ValidationError("Incorrect Credentials")
