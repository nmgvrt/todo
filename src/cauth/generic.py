from django.urls import reverse_lazy

from app.generic import *

from .forms import *
from .models import MyUser

__all__ = [
    'UserListView', 'UserCreateView',
    'UserUpdateView', 'UserDeleteView'
]


class UserListView(ListViewSuper):
    """
    ユーザの一覧を表示するビュー

    アクセス制御 :
      認証されていないときログイン要求
      管理者でないときエラー
    """
    model = MyUser

    def get_queryset(self):
        # 表示するユーザは有効なユーザ
        return self.model.objects.filter(is_active=True)


class UserFormMixin(object):
    model = MyUser
    success_url = reverse_lazy('admin_users')


class UserCreateView(UserFormMixin, CreateViewSuper):
    """
    ユーザを作成するビュー

    アクセス制御 :
      認証されていないときログイン要求
      管理者でないときエラー
    """
    form_class = CreateUserForm


class UserUpdateView(UserFormMixin, ActiveObjectUpdateViewSuper):
    """
    ユーザを編集するビュー

    アクセス制御 :
      指定された pk でユーザが存在しないとき 404
      ユーザがアクティブでないとき 404
      認証されていないときログイン要求
      管理者でないときエラー
    """
    form_class = EditUserForm


class UserDeleteView(UserFormMixin, DeactivateViewSuper):
    """
    ユーザを無効化するビュー

    アクセス制御 :
      指定された pk でユーザが存在しないとき 404
      ユーザがアクティブでないとき 404
      認証されていないときログイン要求
      管理者でないときエラー
    """
    pass
