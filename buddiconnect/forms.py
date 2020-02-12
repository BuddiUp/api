from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    birth_date = forms.DateField()  # help_text='Require. Format: YYYY-MM-DD')
    location = forms.CharField(max_length=5)
    seeker = forms.BooleanField(required=True)
    profile_Image = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2', 'location', 'seeker', 'profile_Image']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ('username', 'birth_date', 'password1', 'password2', 'location','seeker', 'profile_Image')
