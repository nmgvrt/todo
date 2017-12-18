from app.decorators import *

from .models import Tag, Task

__all__ = [
    'test_can_manage_task', 'test_can_manage_tag',
    'can_change_task', 'can_insert_child_task'
]


def test_can_manage_task(user, *args, **kwargs):
    """
    タスクにアクセスする権限(表示, 編集, 削除)があるかを判定する関数
    """
    task = Task.objects.get(pk=kwargs['pk'])
    # 公開タスクなら誰でも許可
    if not task.public:
        # 非公開タスクで対象者でないとき不許可
        if user not in task.unique_users():
            return False

    return True


def can_change_task(*args, **kwargs):
    """
    タスクを変更できるか判定してできなければエラーを表示するデコレータ
    """
    def test_func(user, *args, **kwargs):
        return not Task.objects.get(pk=kwargs['pk']).done

    return user_passes_test(
        test_func, *args,
        error_msg='完了したタスクを変更することはできません.', **kwargs)


def can_insert_child_task(*args, **kwargs):
    """
    子タスクを追加できるか判定してできなければエラーを表示するデコレータ
    """
    def test_func(user, *args, **kwargs):
        return not Task.objects.get(pk=kwargs['pk']).reach_max_depth()

    return user_passes_test(
        test_func, *args,
        error_msg='制限高さに到達したため子タスクを追加できません.', **kwargs)


def test_can_manage_tag(user, *args, **kwargs):
    """
    タグにアクセスする権限(表示, 編集, 削除)があるかを判定する関数
    """
    tag = Tag.objects.get(pk=kwargs['pk'])

    # 共有タグのとき管理者でなければエラー
    if tag.public:
        if not user.is_superuser:
            return False
    # 非共有タグのとき所有者でなければエラー
    else:
        if tag.owner != user:
            return False

    return True
