from rest_framework import serializers
from buddiconnect.models import Profile
from buddiconnect.forms import validate_image
from .models import EmailBackend, CustomUser
import requests
from rest_framework.parsers import MultiPartParser, FormParser
# 241EHLGNGW3A9GRI17OO API KEY


class UserSerializer(serializers.ModelSerializer):
    '''User Serializer'''
    class Meta:
        model = CustomUser
        fields = "__all__"


class ProfileDisplaySerializer(serializers.ModelSerializer):
    """ Profile Serializer """

    class Meta:
        model = Profile
        fields = "__all__"


class UserSearchSerializer(serializers.ModelSerializer):
    max_radius = serializers.CharField(required=True, max_length=3)

    def search(self, request):
        """ Find a faster query solution self note"""
        list = []
        user_profile = Profile.objects.get(id=request.user.id)
        params = {
                'zipcode': user_profile.zipCode,
                'maximumradius': request.data.get('max_radius'),
                'minimumradius': 0,  #  Minimum Radius will stay at 0
                'key': '241EHLGNGW3A9GRI17OO'
        }
        response = requests.get('https://api.zip-codes.com/ZipCodesAPI.svc/1.0/FindZipCodesInRadius?', params)
        result = response.json()
        for zip in result['DataList']:
            profile_list = Profile.objects.filter(zipCode=zip['Code']).exclude(id=user_profile.id)
            for item in profile_list:
                list.append(item)
        return list


class ProfileSerializer(serializers.Serializer):
    '''User Serializer'''
    birth_date = serializers.DateField(required=False)  # help_text='Require. Format: YYYY-MM-DD')
    city = serializers.CharField(required=False, max_length=20)
    state = serializers.CharField(required=False, min_length=2)
    zipCode = serializers.CharField(required=False, min_length=5)
    seeker = serializers.BooleanField(required=False)  # By default its false
    profile_Image = serializers.ImageField(required=False, validators=[validate_image])
    parser_classes = [FormParser, MultiPartParser]

    def save(self, request, filename):

        if self['birth_date'].value is not None:
            self.context['request'].user.profile.birth_date = self.validated_data['birth_date']
        if self['city'].value is not None:
            self.context['request'].user.profile.city = self.validated_data['city']
        if self['state'].value is not None:
            self.context['request'].user.profile.state = self.validated_data['state']
        if self['zipCode'].value is not None:
            self.context['request'].user.profile.zipCode = self.validated_data['zipCode']
        if self['profile_Image'].value is not None:
            self.context['request'].user.profile.profile_Image = validate_image(self.validated_data['profile_Image'])
        if request.data.get('profile_Image', False):
            self.context['request'].user.profile.profile_Image = request.data['profile_Image']
        if self['seeker'].value is False and self.validated_data['seeker'] is True:
            self.context['request'].user.profile.seeker = self.validated_data['seeker']
        self.context['request'].user.profile.save()


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
        user.refresh_from_db()
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
