from rest_framework import serializers
from buddiconnect.models import Profile
from buddiconnect.forms import validate_image
from .models import EmailBackend, CustomUser


class UserSerializer(serializers.ModelSerializer):
    '''User Serializer'''
    class Meta:
        model = CustomUser
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
        fields = ('profile_Image', 'bio', 'city', 'state', 'zipCode', 'email', 'birth_date', 'seeker', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # load the profile instance created by the signal
        # validated_data handles hashing of the password
        CustomUser.objects.create_user(
             validated_data['email'], validated_data['password'])
        # form = SignUpForm(self, instance=user)
        user_profile = CustomUser.objects.get(email=validated_data['email'])
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
        user = CustomUser.objects.get(id=user_profile.profile.id)
        return user


class LoginSerializer(serializers.Serializer):
    '''Login Serializer'''
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = EmailBackend.authenticate(self, **data)

        if user and user.is_active:
            """  If authentication passed, user will be active, else Auth must have failed"""
            return user
        else:
            raise serializers.ValidationError("Incorrect Credentials")
