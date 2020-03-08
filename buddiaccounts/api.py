from rest_framework import generics, permissions
from rest_framework.response import Response
from django.http import HttpResponse
from knox.models import AuthToken

# imports for confirmation email
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from .permissions_file import TokenPermission, account_activation_token
from rest_framework.parsers import MultiPartParser, FormParser
from .models import CustomUser
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ProfileSerializer, UserSearchSerializer, ProfileDisplaySerializer, GetProfileSerializer, AuthenticateUserEmail
import json
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

"""
####### Using PostMan to test #######


"""


class RegisterAPI(generics.GenericAPIView):
    '''
    ####### Register API #######
    - If you want to send more information back to the frontend it goes
    into the return statement
    '''
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # print(serializer.save()) #Uncomment this to debug
        try:
            user = serializer.save()
            user_acc = CustomUser.objects.get(id=user.id)
        except Exception:
            context = {
                'status': '400', 'message': 'ZipCode was invalid or email already exists'
            }
            response = HttpResponse(json.dumps(
                context), content_type='application/json')
            response.status_code = 400
            return response
        # Send confirmation email
        current_site = get_current_site(request)
        email_subject = 'Activate Your Account'
        message = render_to_string('signupPage/activate_account.html', {
            'user': user_acc,
            'domain': current_site.domain,
            'uid': user_acc.userid,
            'token': account_activation_token.make_token(user_acc),
        })
        to_email = serializer.validated_data.get('email')
        email = EmailMessage(email_subject, message, to=[to_email])
        email.send()
        return Response({
            # Sends a serialized user as a response
            "user": ProfileDisplaySerializer(user, context=self.get_serializer_context()).data,
            "default_image": request.build_absolute_uri('/')[:-1].strip("/") + '/photos/default_Images/photos/default-image.png',
            # "default"
            "token": AuthToken.objects.create(user_acc)[1]
        })


class SearchUserAPI(generics.GenericAPIView):

    # permission_classes = [
    #     permissions.IsAuthenticated,
    #     ]
    serializer_class = UserSearchSerializer

    def post(self, request, *args, **kwargs):
        """ Make sure the user is authenticated before search is enabled"""
        serializer = self.get_serializer()
        list = serializer.search(request)
        if list is None:
            """ Third Party API Must have failed or Error message"""
            context = {
                'status': '400', 'Invalid zip or Error with third Party API': 'you can access this view only via ajax'
            }
            response = HttpResponse(json.dumps(context), content_type='application/json')
            response.status_code = 400
            return response
        if len(list) == 0:
            """ No nearby users found """
            context = {
                'status': '420', 'NO USERS NEARBY': 'you can access this view only via ajax'
            }
            response = HttpResponse(json.dumps(
                context), content_type='application/json')
            response.status_code = 400
            return response
        new_list = []
        for profile in list:
            new_list.append(ProfileDisplaySerializer(
                profile, context=self.get_serializer_context()).data)
        return Response({
            # Sends a serialized user as a response
            "userProfiles": new_list,
            "default_image": request.build_absolute_uri('/')[:-1].strip("/") + '/photos/default_Images/photos/default-image.png',
        })


class ProfileAPI(generics.GenericAPIView):
    serializer_class = ProfileSerializer

    permission_classes = [
        TokenPermission,
    ]
    parser_class = (MultiPartParser, FormParser)

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            zipCode = serializer.data['zipcode']
        except Exception:
            zipCode = None
        api_response = serializer.validate_ZipCode(request)
        if api_response is None and zipCode is not None:
            """ No Data for ZipCode"""
            context = {
                'status': '400', 'No Data collected from zipCode': 'you can access this view only via ajax'
            }
            response = HttpResponse(json.dumps(
                context), content_type='application/json')
            response.status_code = 400
            return response
        else:
            serializer.save(request, request.FILES, api_response)
        return Response({
            # Sends a serialized user as a response
            "user": ProfileDisplaySerializer(request.user.profile, context=self.get_serializer_context()).data,
            "default_image": request.build_absolute_uri('/')[:-1].strip("/") + '/photos/default_Images/photos/default-image.png',
        })


class LoginAPI(generics.GenericAPIView):
    '''
    ####### Login API #######
    - If you want to send more information back to the frontend it goes
    into the return statement
    '''
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            # Sends a serialized user as a response
            "user": ProfileDisplaySerializer(user.profile, context=self.get_serializer_context()).data,
            "default_image": request.build_absolute_uri('/')[:-1].strip("/") + '/photos/default_Images/photos/default-image.png',
            "token": AuthToken.objects.create(user)[1]
        })


class UserAPI(generics.RetrieveAPIView):
    '''
    ####### User API #######
    returns:
        - The user that is associated with the request via the token
        This will only display the user's Email
    '''
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = ProfileDisplaySerializer

    def get_object(self):
        return self.request.user.profile


class AuthenticateUserEmailAPI(generics.RetrieveAPIView):
    serializer_class = AuthenticateUserEmail

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        uidb64 = kwargs['uidb64']
        profile = self.serializer_class.authenticate_User(self, token, uidb64)
        if profile is None:
            context = {
                'status': '404', 'No Porfile found': 'Redirect to HomePage'
            }
            response = HttpResponse(json.dumps(context), content_type='application/json')
            response.status_code = 400
            return response
        else:
            return Response({
                # Sends a serialized user as a response

                "status": 200
            })


class ProfileRequestAPI(generics.RetrieveAPIView):
    '''
    ####### Profile Request API #######
    returns:
        - The user that is associated with the request via the token
        This will only display the user's Email
    '''

    serializer_class = GetProfileSerializer

    def get(self, request):
        serializer = self.get_serializer(data=request.data)
        profile = serializer.profile_Request(request)
        if profile is None:
            context = {
                'status': '404', 'No Porfile found': 'Redirect to HomePage'
            }
            response = HttpResponse(json.dumps(context), content_type='application/json')
            response.status_code = 400
            return response
        else:
            print("Responding")
            return Response({
                # Sends a serialized user as a response
                "user": ProfileDisplaySerializer(profile, context=self.get_serializer_context()).data,
                "default_image": request.build_absolute_uri('/')[:-1].strip("/") + '/photos/default_Images/photos/default-image.png',
            })
