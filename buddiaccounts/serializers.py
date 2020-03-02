from rest_framework import serializers
from buddiconnect.models import Profile
from buddiconnect.forms import validate_image
from .models import EmailBackend, CustomUser
from rest_framework.parsers import MultiPartParser, FormParser
from dotenv import load_dotenv
from django.utils import timezone
from helper_functions.helper_functions import capitalize_format, randomUsers
"""  Imports start below this line """
import requests
from django.core.files.base import ContentFile
from PIL import Image
import os
from io import BytesIO
from django.core.files import File
from urllib.parse import parse_qs, urlparse
load_dotenv()  # This will enable to unload the keys secretly


class UserSerializer(serializers.ModelSerializer):
    '''User Serializer'''
    class Meta:
        model = CustomUser
        fields = ('email', 'last_name', 'name', 'userid')


class ProfileDisplaySerializer(serializers.ModelSerializer):
    """ Profile Serializer """

    class Meta:
        model = Profile
        exclude = ('password',)


class UserSearchSerializer(serializers.ModelSerializer):
    """ This will search for users in the area if given or near the user"""
    max_radius = serializers.CharField(required=False, max_length=3)
    zipcode = serializers.CharField(required=False, max_length=6)
    random_users = serializers.BooleanField(required=True)

    def search(self, request):
        """ Find a faster query solution self note"""
        list = []
        max_radius = 0
        if bool(request.data.get('random_users')) is True:
            random_amount = 25  # This is the user amount we want to retrieve
            return randomUsers(random_amount)
        try:
            user_profileID = Profile.objects.get(id=request.user.profile.id).id
        except Exception:
            user_profileID = None
        """ User is not authenticated """
        if request.data.get('max_radius') is not None:
            max_radius = request.data.get('max_radius')
        params = {
            'zipcode': request.data.get('zipcode'),
            'maximumradius': max_radius,
            'minimumradius': 0,  # Minimum Radius will stay at 0
            'key': os.getenv('zipCodekey', 'lkadnflksandl%&*^&*#lkjlkasdj<..,(++)')
        }
        try:
            response = requests.get(
                'https://api.zip-codes.com/ZipCodesAPI.svc/1.0/FindZipCodesInRadius?', params)
            result = response.json()
        except Exception:
            print("Error in Third Party API in User Search API")
            return None
        if result is None or len(result) <= 1:
            try:
                if result['Error'] is not None:
                    print("Got the error")
                    return None
            except Exception:
                """ There is data in the result"""
                pass
        for zip in result['DataList']:
            profile_list = Profile.objects.filter(zipcode=int(zip['Code'])).exclude(id=user_profileID, seeker=False)
            for item in profile_list:
                list.append(item)
        # if len(list) == 0:
        #     """ No profiles near zipCode and readius given"""
        #     return None
        return list


class ProfileSerializer(serializers.Serializer):
    '''User Serializer'''
    birth_date = serializers.DateField(
        required=False)  # help_text='Require. Format: YYYY-MM-DD')
    zipcode = serializers.CharField(required=False, min_length=5)
    seeker = serializers.BooleanField(required=False)  # By default its false
    profile_Image = serializers.ImageField(
        required=False, validators=[validate_image])
    parser_classes = [FormParser, MultiPartParser]
    name = serializers.CharField(required=False, max_length=25)
    last_name = serializers.CharField(required=False, max_length=50)

    def validate_ZipCode(self, request):
        try:
            params = {
                'key': os.getenv('zipCodekey', 'lkadnflksandl%&*^&*#lkjlkasdj<..,(++)')
            }
            response = requests.get(
                'https://api.zip-codes.com/ZipCodesAPI.svc/1.0/QuickGetZipCodeDetails/{}?'.format(self['zipcode'].value), params)
            result = response.json()
        except Exception:
            print("Could not Update city and state by ZipCode in update API")
        if result is None or len(result) <= 1:
            try:
                if result['Error'] is not None:
                    return None
            except Exception:
                """ There is data in the result or result call is empty"""
                if len(result) == 0:
                    return None
        return result

    def save(self, request, filename, result):

        if self['birth_date'].value is not None:
            self.context['request'].user.profile.birth_date = self.validated_data['birth_date']
        if self['name'].value is not None:
            self.context['request'].user.profile.name = capitalize_format(self.validated_data['name'])
        if self['last_name'].value is not None:
            self.context['request'].user.profile.last_name = capitalize_format(self.validated_data['last_name'])
        if self['zipcode'].value is not None:
            """ Update both state and city when ZipCode is updated"""
            self.context['request'].user.profile.city = capitalize_format(result['City'])
            self.context['request'].user.profile.state = result['State']
            self.context['request'].user.profile.zipcode = self.validated_data['zipcode']
        if self['profile_Image'].value is not None:
            self.context['request'].user.profile.profile_Image = validate_image(
                self.validated_data['profile_Image'])
        if request.data.get('profile_Image', False):
            self.context['request'].user.profile.profile_Image = request.data['profile_Image']
        if self['seeker'].value is not None:
            self.context['request'].user.profile.seeker = self.validated_data['seeker']
        self.context['request'].user.profile.save()


class RegisterSerializer(serializers.ModelSerializer):
    '''Register Serializer'''
    class Meta:
        model = Profile
        fields = ('email', 'password', 'zipcode', 'name', 'last_name',
                  'gender', 'birth_day', 'birth_month', 'birth_year')
        extra_kwargs = {'password': {'write_only': True}}

    def absolute(request):
        urls = {
            'ABSOLUTE_ROOT': request.build_absolute_uri('/')[:-1].strip("/"),
            'ABSOLUTE_ROOT_URL': request.build_absolute_uri('/').strip("/"),
            }

        return urls

    def create(self, validated_data):
        # load the profile instance created by the signal
        try:
            params = {
                'key': os.getenv('zipCodekey', '---202992928--')
            }
            response = requests.get(
                'https://api.zip-codes.com/ZipCodesAPI.svc/1.0/QuickGetZipCodeDetails/{}?'.format(validated_data['zipcode']), params)
            result = response.json()
        except Exception:
            """ API RETURNED AN ERROR MESSAGE"""
            print("Error 1")
            return None
        if result is None or len(result) <= 1:
            try:
                if result['Error'] is not None:
                    print("Got the error", result)
                    return None
            except Exception:
                """ There is data in the result or its empty"""
                if len(result) == 0:
                    print("Error 2")
                    return None
        user = CustomUser.objects.create_user(
             validated_data['email'], validated_data['password'])
        user.name = capitalize_format(validated_data['name'])
        user.last_name = capitalize_format(validated_data['last_name'])
        user.refresh_from_db()
        user.profile.zipcode = validated_data['zipcode']
        user.profile.gender = validated_data['gender']
        user.profile.name = capitalize_format(validated_data['name'])
        user.profile.last_name = capitalize_format(validated_data['last_name'])
        user.profile.birth_day = validated_data['birth_day']
        user.profile.birth_month = validated_data['birth_month']
        user.profile.birth_year = validated_data['birth_year']
        user.profile.email = validated_data['email']
        user.profile.state = result['State']
        user.profile.city = capitalize_format(result['City'])
        user.profile.age = timezone.now().year - int(validated_data['birth_year'])
        im = Image.open(r"api/default_Images/photos/default-image.png")
        im.convert('RGB') # convert mode
        # im.thumbnail((200, 200)) # resize image
        thumb_io = BytesIO() # create a BytesIO object
        im.save(thumb_io, 'PNG', quality=100) # save image to BytesIO object
        thumbnail = File(thumb_io, name='default-image.png') # create a django friendly File object
        user.profile.profile_Image = thumbnail
        #  Inserting shutil
        user.profile.profile_urlfield = self.context['request'].build_absolute_uri('/')[:-1].strip("/") + '/user/?' + 'userid=' + user.userid
        user.profile.save()
        return user


class LoginSerializer(serializers.Serializer):
    '''Login Serializer'''
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = EmailBackend.authenticate(self, **data)
        print("This is the user", user)
        if user and user.is_active:
            print("Authenticated")
            """  If authentication passed, user will be active, else Auth must have failed"""
            user.profile.age = timezone.now().year - int(user.profile.birth_year)
            user.profile.save()
            return user
        else:
            raise serializers.ValidationError("Incorrect Credentials")


class GetProfileSerializer(serializers.Serializer):
    def profile_Request(self, request):
        url = request.GET.urlencode()
        try:
            query_dict = parse_qs(url)
            profile = CustomUser.objects.get(userid=query_dict['userid'][0])
            return profile.profile
        except Exception:
            """ No data in url"""
            return None
