from app.forms import *

from .form_fields import *
from .models import Tag, UserGroup, Task


__all__ = [
    'RootTaskForm', 'ChildTaskForm',
    'EditChildTaskForm', 'FinishTaskForm',
    'TagForm', 'UserGroupForm',
]


class ToDoCustomModelForm(CustomModelForm):
    additional_keys = ['user', 'task']


class RootTaskForm(ToDoCustomModelForm):
    """
    親タスク用フォーム
    users は UserGroupMultipleChoiceField で制限
    tags は TagMultipleChoiceField で制限

    form 上の users は ajax で制御
      ユーザ単位の指定用 json : views.json_usergroup_user
      グループ単位の指定用 json : views.json_usergroup_group

    form 上の tags は ajax で制御
      共有タグの指定用 json : views.json_tag_public
      非共有タグの指定用 json : views.json_tag_private
    """
    required = ['users', 'priority', 'repeat']

    class Meta:
        model = Task
        fields = [
            'name', 'description', 'deadline', 'repeat',
            'priority', 'public', 'tags', 'users']
        field_classes = {
            'users': UserGroupMultipleChoiceField,
            'tags': TagMultipleChoiceField,
        }


class ChildTaskForm(ToDoCustomModelForm):
    """
    子タスク用フォーム
    users は ChildsUserGroupMultipleChoiceField で制限

    form 上の users は ajax で制御
      ユーザ単位の指定用 json : views.json_usergroup_user_child
      グループ単位の指定用 json : views.json_usergroup_group_child
    """
    class Meta:
        model = Task
        fields = ['name', 'description', 'deadline', 'priority', 'users']
        field_classes = {
            'users': ChildsUserGroupMultipleChoiceField,
        }


class EditChildTaskForm(ChildTaskForm):
    """
    子タスク編集用フォーム
    users は EditChildsUserGroupMultipleChoiceField で制限

    form 上の users は ajax で制御
      ユーザ単位の指定用 json : views.json_usergroup_user_child_edit
      グループ単位の指定用 json : views.json_usergroup_group_child_edit
    """
    class Meta(ChildTaskForm.Meta):
        field_classes = {
            'users': EditChildsUserGroupMultipleChoiceField,
        }


class FinishTaskForm(ToDoCustomModelForm):
    """
    タスク完了用フォーム
    users は DoneUserMultipleChoiceField で制限
    """
    class Meta:
        model = Task
        fields = ['done_users']
        field_classes = {
            'done_users': DoneUserMultipleChoiceField,
        }


class TagForm(ToDoCustomModelForm):
    """
    タグ用フォーム
    """
    required = ['color']

    class Meta:
        model = Tag
        fields = ['name', 'color']


class UserGroupForm(ToDoCustomModelForm):
    """
    ユーザグループ用フォーム
    """
    required = ['users']

    class Meta:
        model = UserGroup
        fields = ['name', 'users']
        field_classes = {
            'users': ActiveUserMultipleChoiceField,
        }
