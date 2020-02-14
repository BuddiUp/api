
from django.shortcuts import render, redirect
from django.views import View
from django.template import loader
from .forms import SignUpForm
from .models import Profile
from .serializers import ProfileSerializer
from django.http import HttpResponse
from rest_framework import generics
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
# Create your views here.


class Homepage(View):
    """ Class subview of View to Test homePage App"""
    def get(self, request):
        #  updateApp()  # Only use this function if you want to refresh the App with new Articles
        template = loader.get_template('home_Screen/home.html')  #  Templates folder needs to be within App is True
        return HttpResponse(template.render({}, request))


class Profilepage(View):
    """ This will display the profile model in Database"""
    def get(self, request):
        """ View profile page on a get way  """
        profile_Object = Profile.objects.get(user=request.user)
        if profile_Object.profile_Image:
            print("Exists")
        else:
            print("Nothing here")
        print("Current Image:", profile_Object.profile_Image.url)
        template = loader.get_template('profile_Page/profile_page.html')  #  Templates folder needs to be within App is True
        return HttpResponse(template.render({"profile": profile_Object, "image": profile_Object.profile_Image.url}, request))

    def post(self, request):
        pass


def signout(request):
    print("User", request.user)
    logout(request)
    return redirect('homePage')


class zipCodeSearch(View):
    """ Parsing through profiles within the area """
    def get(self, request):
        pass

    def post(self, request):
        pass


class ProfileAPICalls(generics.ListCreateAPIView):
    """Adding API call here """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


def signup(request):
    """ This will prompt User Creation and with form"""
    if request.method == 'POST':
        print("Request is post")
        form = SignUpForm(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            """ If the form was created successfully"""
            print("Form was a success")
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.profile.seeker = form.cleaned_data.get('seeker')
            user.profile.city = form.cleaned_data.get('city')
            user.profile.state = form.cleaned_data.get('state')
            user.profile.zipCode = form.cleaned_data.get('zipCode')

            user.profile.profile_Image = form.clean_image()
            print("This is what we are saving:", form.cleaned_data.get('profile_Image'))
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('homePage')
        else:
            print("Starting brand New")
            form = SignUpForm(request.POST)
    if request.method == 'GET':
        print("Landed on Signup Page")
        form = SignUpForm()
    return render(request, 'signupPage/signupPage.html', {'form': form})
