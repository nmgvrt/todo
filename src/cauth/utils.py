from django.apps import apps
from django.conf import settings


def UserCls():
    return apps.get_model('cauth', settings.AUTH_USER_MODEL.split('.')[-1])
