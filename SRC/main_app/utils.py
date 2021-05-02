import datetime
import jwt

from django.conf import settings

'''
    Authentication access token, managed by JWT
'''


def generate_access_token(user):
    """
        The method takes only user(argument), then it makes encoded data,
        this data includes(user ID, expire time[7 days after token generation], the current time),
        it uses HS256 encoded algorithm.
    """
    access_token_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=6, hours=23, minutes=59),
        'iat': datetime.datetime.utcnow()
    }
    access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')
    return access_token


def generate_refresh_token(user, token_version):
    """
        This method also managed by JWT, but its expire time are higher than the normal access token,
        it make the owen session is a month.
    """
    refresh_token_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
        'iat': datetime.datetime.utcnow(),
        'token': token_version
    }
    refresh_token = jwt.encode(
        refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')

    return refresh_token
