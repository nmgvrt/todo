from functools import wraps

from django.http import Http404
from django.contrib import messages
from django.shortcuts import reverse, redirect

__all__ = [
    'raise_error', 'user_passes_test', 'user_passes_test_404',
    'raise_404_if_not_exists', 'raise_404_if_deleted',
    'is_authenticated', 'is_superuser', 'can_manage_object'
]


def raise_error(request, msg, name='error'):
    messages.error(request, msg)

    return redirect(reverse(name))


def user_passes_test(test_func, *args, error_msg=None, **kwargs):
    def decorator(view_func, *args, **kwargs):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user, *args, **kwargs):
                return view_func(request, *args, **kwargs)
            msg = error_msg or 'ページにアクセスする権限がありません.'

            return raise_error(request, msg)
        return _wrapped_view
    return decorator


def user_passes_test_404(test_func, *args, **kwargs):
    def decorator(view_func, *args, **kwargs):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user, *args, **kwargs):
                return view_func(request, *args, **kwargs)

            raise Http404
        return _wrapped_view
    return decorator


def raise_404_if_not_exists(cls, *args, **kwargs):
    def test_func(user, *args, **kwargs):
        try:
            cls.objects.get(pk=kwargs['pk'])
            return True
        except:
            return False

    return user_passes_test_404(test_func, *args, **kwargs)


def raise_404_if_deleted(cls, *args, **kwargs):
    def test_func(user, *args, **kwargs):
        try:
            return cls.objects.get(pk=kwargs['pk']).is_active
        except:
            return False

    return user_passes_test_404(test_func, *args, **kwargs)


def is_authenticated(user, *args, **kwargs):
    return user.is_authenticated


def is_superuser(user, *args, **kwargs):
    return user.is_superuser


def can_manage_object(test_func, *args, **kwargs):
    """
    オブジェクトにアクセスできるかを test_func で判定し,
    権限がなければエラーを表示するデコレータ
    """
    return user_passes_test(
        test_func, *args, error_msg='このオブジェクトにアクセスする権限がありません.', **kwargs)
