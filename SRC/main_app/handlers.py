from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, status
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import exception_handler, set_rollback

from urllib3.packages import six


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response


class UniqueEmailException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Error Message'


def exception_handler(exc, context):
    # Custom exception handler
    if isinstance(exc, UniqueEmailException):
        set_rollback()
        data = {'detail': exc.detail}
        return Response(data, status=exc.status_code)

    elif isinstance(exc, (exceptions.APIException, ValidationError)):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if hasattr(exc, 'error_dict') and isinstance(exc, ValidationError):
            exc.status_code = HTTP_400_BAD_REQUEST
            data = exc.message_dict
        elif isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {'detail': exc.detail}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    elif isinstance(exc, Http404):
        msg = _('Not found.')
        data = {'detail': six.text_type(msg)}

        set_rollback()
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    return None
