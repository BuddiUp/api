from buddiconnect.models import Profile
from buddiaccounts.models import CustomUser
import random
import uuid
import base64


def capitalize_format(string):
    """ Capitalize first letter of every word """
    words = string.split()
    result = ""
    # for word in words:
    #     result += word.capitalize()
    for index in range(len(words)):
        if (index + 1 >= len(words)) is False:
            result += words[index].capitalize() + " "
        else:
            result += words[index].capitalize()
    return result


def randomUsers(amount):
    """ Grab a random set of users set my amount"""
    profiles = Profile.objects.all().filter(seeker=True)
    list_profiles = []
    cap = len(Profile.objects.all().filter(seeker=True))
    while amount > 0:
        random_number = random.randint(0, len(profiles)-1)
        if profiles[random_number] in list_profiles:
            if len(list_profiles) == cap:
                break
            else:
                continue
        list_profiles.append(profiles[random_number])
        amount -= 1
    return list_profiles


def createGUID():
    while True:
        short_UUID = base64.urlsafe_b64encode(uuid.uuid1().bytes).rstrip(b'=').decode('ascii')
        if CustomUser.objects.get(userid=short_UUID):
            break
pass
