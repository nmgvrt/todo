from django.db.models import Q
from django.forms import models

from app.form_fields import *

from cauth.models import MyUser

from .models import Tag, UserGroup

__all__ = [
    'UserGroupMultipleChoiceField',
    'TagMultipleChoiceField',
    'ChildsUserGroupMultipleChoiceField',
    'EditChildsUserGroupMultipleChoiceField',
    'DoneUserMultipleChoiceField',
    'ActiveUserMultipleChoiceField'
]


class UserGroupMultipleChoiceField(
    models.ModelMultipleChoiceField, CustomFormFieldMixin
):
    """
    ルートタスクの users 用フォームフィールド
    ルートタスクの users は有効な UserGroup の組み合わせなら良い
    """
    def set_new_queryset(self, *args, **kwargs):
        self.queryset = UserGroup.objects.filter(is_active=True)


class TagMultipleChoiceField(
    models.ModelMultipleChoiceField, CustomFormFieldMixin
):
    """
    ルートタスクの tags 用フォームフィールド
    ルートタスクの tags は自分の使える Tag (MyUser.usable_tags)
    の組み合わせなら良い
    """
    def set_new_queryset(self, *args, **kwargs):
        return Tag.objects.filter(pk__in=self.user.usable_tags()).distinct()


class ChildsUserGroupMultipleChoiceField(
    models.ModelMultipleChoiceField, CustomFormFieldMixin
):
    """
    子タスクの users 用フォームフィールド
    子タスクの users は選択可能な UserGroup
    (Task.selectable_usergroups)の組み合わせなら良い
    """
    def set_new_queryset(self, *args, **kwargs):
        self.queryset = self.task.selectable_usergroups()


class EditChildsUserGroupMultipleChoiceField(
    models.ModelMultipleChoiceField, CustomFormFieldMixin
):
    """
    子タスクの users 編集フォームフィールド
    子タスクの users は親タスクの選択可能な UserGroup
    (Task.selectable_usergroups)の組み合わせなら良い
    """
    def set_new_queryset(self, *args, **kwargs):
        self.queryset = self.task.get_parent().selectable_usergroups()


class DoneUserMultipleChoiceField(
    models.ModelMultipleChoiceField, CustomFormFieldMixin
):
    """
    タスク完了者指定用フォームフィールド
    タスクを完了できるのはタスクの対象者
    """
    def set_new_queryset(self, *args, **kwargs):
        self.queryset = self.task.unique_users()


class ActiveUserMultipleChoiceField(
    models.ModelMultipleChoiceField, CustomFormFieldMixin
):
    """
    ユーザグループの参加者指定用フォームフィールド
    参加者に指定できるのは有効なユーザ
    """
    def set_new_queryset(self, *args, **kwargs):
        self.queryset = MyUser.objects.filter(is_active=True)
