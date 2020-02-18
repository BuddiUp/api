#  This is where we will have our custom permissions

from rest_framework import permissions
from .models import CustomUser
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
