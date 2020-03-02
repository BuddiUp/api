from django.conf.urls import url
from django.urls import path
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.staticfiles.urls import static

# This syntax imports all of the functions and classes
# inside the views.py in the same folder.
from . import views
urlpatterns = [
    path('', views.Homepage.as_view(), name='homePage'),
    path('accounts/register', views.signup, name='signup'),
    path('signout', views.signout, name='signout'),
    path('profile', views.Profilepage.as_view(), name='profilePage'),
    path('search', views.zipCodeSearch.as_view(), name='zipCodeSearch'),
    path('api/profiles', views.ProfileAPICalls.as_view())
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
