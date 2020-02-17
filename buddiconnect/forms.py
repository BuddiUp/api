from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import cv2


def validate_image(image):
    """ This will Cap the Image to 1500 KB"""
    file_size = image.size
    limit_kb = 1500 * 30
    if file_size > limit_kb:
        raise ValidationError("Max size of file is %s KB" % limit_kb)
    return image


def compareImages(ImageOne, ImageTwo):
    difference = cv2.subtract(ImageOne, ImageTwo)
    b, g, r = cv2.split(difference)
    if not cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
        return False
    else:
        return True


class SignUpForm(UserCreationForm, forms.Form):

    birth_date = forms.DateField()  # help_text='Require. Format: YYYY-MM-DD')
    city = forms.CharField(max_length=20)
    state = forms.CharField(max_length=2)
    zipCode = forms.CharField(max_length=5)
    seeker = forms.BooleanField(required=True)
    profile_Image = forms.ImageField(validators=[validate_image])

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2', 'city', 'seeker', 'profile_Image' , 'state', 'zipCode']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ('username', 'birth_date', 'password1', 'password2', 'city' ,'seeker', 'profile_Image', 'state', 'zipCode')
