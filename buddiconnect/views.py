
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

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

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
            print("This is the form", user)
            user.refresh_from_db()  # load the profile instance created by the signal
            # user.profile.birth_date = form.cleaned_data.get('birth_date')
            # user.profile.seeker = form.cleaned_data.get('seeker')
            # user.profile.city = form.cleaned_data.get('city')
            # user.profile.state = form.cleaned_data.get('state')
            # user.profile.zipCode = form.cleaned_data.get('zipCode')
            # user.profile.profile_Image = form.cleaned_data.get('profile_Image')
            # print("This is what we are saving:", form.cleaned_data.get('profile_Image'))
            user.save()

            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=user.username, password=raw_password)
            # login(request, user)
            # return redirect('homePage')
            
            # Send confirmation email
            current_site = get_current_site(request)
            email_subject = 'Activate Your Account'
            message = render_to_string('signupPage/activate_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            return HttpResponse('We have sent you an email, please confirm your email address to complete registration')
        else:
            print("Starting brand New")
            form = SignUpForm(request.POST)
    if request.method == 'GET':
        print("Landed on Signup Page")
        form = SignUpForm()
    return render(request, 'signupPage/signupPage.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Your account has been activated successfully')
    else:
        return HttpResponse('Activation link is invalid!')
