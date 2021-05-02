from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions


# Check if user is Admin staff
def is_staff(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_staff:
            raise exceptions.PermissionDenied(_('Not authorized'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


# Check if user is Customer staff
def is_normal(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.is_staff:
            raise exceptions.PermissionDenied(_('Not authorized'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
