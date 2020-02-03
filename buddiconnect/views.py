
from django.shortcuts import render, redirect
from django.views import View
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
# Create your views here.


class Homepage(View):
    """ Class subview of View to Test homePage App"""
    def get(self, request):
        #  updateApp()  # Only use this function if you want to refresh the App with new Articles
        template = loader.get_template('home_Screen/home.html')  #  Templates folder needs to be within App is True
        return HttpResponse(template.render({}, request))


def signup(request):
    """ This will prompt User Creation and with form"""
    if request.method == 'POST':
        print("Request is post")
        form = UserCreationForm(request.POST)
    if form.is_valid():
        form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(request, user)
        return redirect('homePage')
    else:
        form = UserCreationForm()
    return render(request, 'signupPage/signupPage.html', {'form': form})
