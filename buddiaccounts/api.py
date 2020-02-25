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
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ProfileSerializer, UserSearchSerializer, ProfileDisplaySerializer
import json
'''
####### Using PostMan to test #######
BODY REFERENCE:
    !!!!!!!! READ !!!!!!!!
    - If you're doing RegisterAPI you can copy the whole thing below
    - If you're doing LoginAPI REMOVE the email from the body
    {
        "username": "test",
        "email": "test@gmail.com",
        "password": "12345"
    }

RegisterAPI:
    - Open a new tab
    - Set to POST request with the URL: http://127.0.0.1:8000/api/auth/register
    - Inside HEADERS:
        - KEY: Content-Type
        - VALUE: application/json
    - Go to BODY, hit RAW and add (refer to BODY REFERENCE)
    - Hit send
LoginAPI:
    - Open a new tab
    - Set to POST request with the URL: http://127.0.0.1:8000/api/auth/login
    - Inside HEADERS:
        - KEY: Content-Type
        - VALUE: application/json
    - Go to BODY, hit RAW and add (refer to BODY REFERENCE)
    - Hit send
UserAPI:
    - Open a new tab
    - Set to GET request with the URL: http://127.0.0.1:8000/api/auth/user
    - Inside HEADERS:
        - KEY: Authorization
        - VALUE: Token (get token from LoginAPI)
    - Hit send
'''
'''  ADDED ZIPCODE VALIDATION WITH INCREASE SPEED, WILL OPTIMIZE SOON
    2/22/2020
'''


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
        try:
            user = serializer.save()
        except Exception:
            """ Check if the zipCode caused the problem"""
            """ Third Party API Must have failed"""
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
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        to_email = serializer.validated_data.get('email')
        email = EmailMessage(email_subject, message, to=[to_email])
        email.send()

        return Response({
            # Sends a serialized user as a response
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
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
        if list is None or len(list) == 0:
            """ Third Party API Must have failed"""
            context = {
                'status': '400', 'No Data collected from zipCode': 'you can access this view only via ajax'
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
