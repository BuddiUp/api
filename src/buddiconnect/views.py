# from django.shortcuts import render
from django.views import View
from django.template import loader
from django.http import HttpResponse
# Create your views here.


class Homepage(View):
    """ Class subview of View to Test homePage App"""
    def get(self, request):
        #  updateApp()  # Only use this function if you want to refresh the App with new Articles
        template = loader.get_template('home_Screen/home.html')  #  Templates folder needs to be within App is True
        return HttpResponse(template.render({}, request))
