from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from .permissions_file import TokenPermission
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ProfileSerializer, UserSearchSerializer, ProfileDisplaySerializer

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
        user = serializer.save()
        return Response({
            # Sends a serialized user as a response
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class SearchUserAPI(generics.GenericAPIView):

    permission_classes = [
        permissions.IsAuthenticated,
        ]
    serializer_class = UserSearchSerializer

    def post(self, request, *args, **kwargs):
        """ Make sure the user is authenticated before search is enabled"""
        serializer = self.get_serializer()
        list = serializer.search(request)
        new_list = []
        for profile in list:
            new_list.append(ProfileDisplaySerializer(profile, context=self.get_serializer_context()).data)
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
        serializer.save(request, request.FILES)
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
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class UserAPI(generics.RetrieveAPIView):
    '''
    ####### User API #######
    returns:
        - The user that is associated with the request via the token
    '''
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile
