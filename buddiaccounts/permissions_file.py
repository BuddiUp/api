#  This is where we will have our custom permissions

from rest_framework import permissions

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

from .models import CustomUser


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()


# class BlacklistPermission(permissions.BasePermission):
#     """
#     Global permission check for blacklisted IPs.
#     """
#
#     def has_permission(self, request, view):
#         ip_addr = request.META['REMOTE_ADDR']
#         blacklisted = Blacklist.objects.filter(ip_addr=ip_addr).exists()
#         return not blacklisted


class TokenPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        AuthUser = CustomUser.objects.get(email=request.user.email)
        if AuthUser is not None:
            return True
        return False
