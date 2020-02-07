from django.conf.urls import url
from django.urls import path
# This syntax imports all of the functions and classes
# inside the views.py in the same folder.
from . import views
urlpatterns = [
    path('', views.Homepage.as_view(), name='homePage'),
    path('signup', views.signup, name='signup'),
    path('signout', views.signout, name='signout')
]
