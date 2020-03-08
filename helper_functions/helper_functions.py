from buddiconnect.models import Profile
import random
from django.utils import timezone

""" Optimize these functions when bare bone of the project are functional  """


def capitalize_format(string):
    """ Capitalize first letter of every word """
    words = string.split()
    result = ""
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
    try:
        while amount > 0:
            random_number = random.randint(0, len(profiles)-1)
            if profiles[random_number] in list_profiles:
                if len(list_profiles) == cap:
                    break
                else:
                    continue
            list_profiles.append(profiles[random_number])
            amount -= 1
    except Exception:
        """ NO USERS WITHIN THE DEFAULT RADIUS"""
        return list_profiles
    return list_profiles


def userAge(month, day, year):
    month = int(month)
    day = int(day)
    year = int(year)
    if month >= timezone.now().month:
        if month == timezone.now().month:
            if day > timezone.now().day:
                age = (timezone.now().year - int(year)) - 1
                return age
            else:
                age = (timezone.now().year - int(year))
                return age
        else:
            age = (timezone.now().year - int(year)) - 1
            return age
    else:
        age = (timezone.now().year - int(year))
        return age
