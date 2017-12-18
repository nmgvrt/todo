from django.http import Http404
from django.conf import settings
from django.urls import reverse_lazy
from django.db.models.query import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import PasswordChangeForm

from app.decorators import *
from app.generic import *

from .forms import *
from .models import Tag, UserGroup, Task
from .decorators import *


@method_decorator(can_manage_object(test_can_manage_task), name='dispatch')
class TaskDetailView(ActiveObjectDetailView):
    """
    タスクの詳細

    アクセス制御 :
      指定された pk でタスクが存在しないとき 404
      タスクがアクティブでないとき 404
      認証されていないときログイン要求
      タスクへアクセスする権限がないときエラー
    """
    model = Task


class TaskListView(ListViewAuth):
    """
    ルートタスクを締め切り順にソートして表示する ListView
    """
    model = Task
    paginate_by = settings.PAGINATE_BY
    mode = 'none'

    def get_filter(self):
        return Q()

    def get_queryset(self):
        """
        有効なルートタスクに特定のフィルタをかけて返す
        """
        self._error = None
        self._tag = None
        self._group = None

        # 有効なルートタスクに派生クラスで定義されるフィルタをかける
        tasks = self.model.active_objects(
            ).filter(Q(level=0) & self.get_filter())
        self.unfiltered_tasks = tasks

        # Tag が指定されたとき
        if 'tag_pk' in self.kwargs:
            try:
                # 受け取った pk でタグが存在し,
                # タグがユーザの使用可能なタグの中にあればフィルタ
                # なければエラーを起こすためのフラグを立てる
                self._tag = Tag.objects.get(pk=int(self.kwargs['tag_pk']))
                if self._tag.is_active:
                    if self._tag in self.request.user.usable_tags():
                        tasks = tasks.filter(tags=self._tag)
                    else:
                        self._error = '指定されたタグにアクセスする権限がありません.'
                else:
                    self._error = '指定されたタグは存在しません.'
            except:
                self._error = '指定されたタグは存在しません.'

        # UserGroup が指定されたとき
        if 'group_pk' in self.kwargs:
            try:
                # 受け取った pk でユーザグループが存在すればフィルタ
                # なければエラーを起こすためのフラグを立てる
                self._group = UserGroup.objects.get(
                    pk=int(self.kwargs['group_pk']))
                if self._group.is_active:
                    if self._group.auto_created:
                        tasks = tasks.filter(
                            users__users=self._group.users.first())
                    else:
                        tasks = tasks.filter(users=self._group)
                else:
                    self._error = '指定されたユーザグループは存在しません.'
            except:
                self._error = '指定されたユーザグループは存在しません.'

        # 重複除去とソート
        return tasks.distinct().order_by('-done', 'earliest')

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)

        unfiltered = Task.objects.filter(pk__in=self.unfiltered_tasks)

        # タスクリストページのフィルタ用タグリスト

        # タスクに登録されたタグ
        tags_pk = unfiltered.values_list(
            'tags__pk', flat=True).distinct()
        public_tags = Tag.objects.filter(
            pk__in=tags_pk, public=True).distinct()
        private_tags = Tag.objects.filter(
            pk__in=tags_pk, public=False).distinct()

        # タスクリストページのフィルタ用ユーザグループリスト

        # タスクに登録されたユーザグループ
        groups_pk = unfiltered.values_list(
            'users__pk', flat=True).distinct()
        groups = UserGroup.objects.filter(
            pk__in=groups_pk, auto_created=False).distinct()

        # タスクの対象者
        groups_users_pk = unfiltered.values_list(
            'users__users__pk', flat=True).distinct()
        users = UserGroup.objects.filter(
            users__pk__in=groups_users_pk, auto_created=True).distinct()

        data.update({
            'tag': self._tag, 'group': self._group, 'mode': self.mode,
            'public_tags': public_tags, 'private_tags': private_tags,
            'groups': groups, 'users': users,
        })

        return data

    def render_to_response(self, *args, **kwargs):
        """
        エラーがあればエラー画面に転送
        """
        if self._error is None:
            return super().render_to_response(*args, **kwargs)
        else:
            return raise_error(self.request, self._error)


class PublicTaskListView(TaskListView):
    """
    公開されているタスクのルートを表示する TaskListView
    """
    mode = 'public'

    def get_filter(self):
        # 公開されている未完了のタスクに限定
        return Q(done=False, public=True)


class FinishedPublicTaskListView(TaskListView):
    """
    完了した公開タスクのルートを表示する TaskListView
    """
    mode = 'finished_public'

    def get_filter(self):
        # 完了した公開タスクに限定
        return Q(done=True, public=True)


class MyTaskListView(TaskListView):
    """
    自分のタスクのルートを表示する TaskListView
    """
    mode = 'my_task'

    def get_filter(self):
        # 未完了の自分の所属するグループが対象に含まれるタスクに限定
        return Q(done=False, users__in=self.request.user.own_groups())


class FinishedMyTaskListView(TaskListView):
    """
    自分のタスクのルートを表示する TaskListView
    """
    mode = 'finished_my_task'

    def get_filter(self):
        # 完了した自分の所属するグループが対象に含まれるタスクに限定
        return Q(done=True, users__in=self.request.user.own_groups())


class UserGroupListView(ListViewSuper):
    """
    ユーザグループの一覧を表示するビュー

    アクセス制御 :
      認証されていないときログイン要求
      管理者でないときエラー
    """
    model = UserGroup

    def get_queryset(self):
        # 表示するユーザグループは有効でシステム管理外のユーザグループ
        return self.model.objects.filter(is_active=True, auto_created=False)


class UserGroupCreateView(CreateViewSuper):
    """
    ユーザグループを作成するビュー

    アクセス制御 :
      認証されていないときログイン要求
      管理者でないときエラー
    """
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('admin_usergroups')


class PublicTagListView(ListViewSuper):
    """
    共有タグの一覧を表示するビュー
    """
    model = Tag

    def get_queryset(self):
        # 共有タグは有効で public なタグ
        return self.model.objects.filter(is_active=True, public=True)


class MyTagListView(ListViewAuth):
    """
    自分のタグの一覧を表示するビュー
    """
    model = Tag

    def get_queryset(self):
        # 自分のタグは有効で自身の所有するタグ
        return self.model.objects.filter(
            is_active=True, owner=self.request.user)


class TagNextUrlMixin(object):
    """
    タグ操作時の success_url を返す Mixin
    """
    def get_success_url(self):
        if self.object.public:
            return reverse_lazy('admin_tags')
        else:
            return reverse_lazy('my_tags')


class AdminTagCreateView(TagNextUrlMixin, CreateViewSuper):
    """
    共有タグを作成するビュー
    フォームは TagForm
    タグ色の初期値は色オブジェクトのひとつ目
    作成時には admin_tags へリダイレクト

    アクセス制御 :
      認証されていないときログイン要求
      管理者でないときエラー
    """
    model = Tag
    form_class = TagForm
    initial = {'color': 1}

    def set_initial(self, instance):
        # 共有タグは public
        instance.public = True


class MyTagCreateView(TagNextUrlMixin, CreateViewAuth):
    """
    自分のタグを作成するビュー
    フォームは TagForm
    タグ色の初期値は色オブジェクトのひとつ目
    作成時には my_tags へリダイレクト

    アクセス制御 :
      認証されていないときログイン要求
    """
    model = Tag
    form_class = TagForm
    initial = {'color': 1}

    def set_initial(self, instance):
        # 自分のタグは public でない
        instance.public = False
        # 所有者は自分
        instance.owner = self.request.user


@method_decorator(can_manage_object(test_can_manage_tag), name='dispatch')
class TagUpdateView(TagNextUrlMixin, ActiveObjectUpdateViewAuth):
    """
    タグの編集

    アクセス制御 :
      指定された pk でタグが存在しないとき 404
      タグがアクティブでないとき 404
      認証されていないときログイン要求
      タグへアクセスする権限がないときエラー
    """
    model = Tag
    form_class = TagForm


@method_decorator(can_manage_object(test_can_manage_tag), name='dispatch')
class TagDeleteView(TagNextUrlMixin, DeactivateViewAuth):
    """
    タグの無効化

    アクセス制御 :
      指定された pk でタグが存在しないとき 404
      タグがアクティブでないとき 404
      認証されていないときログイン要求
      タグへアクセスする権限がないときエラー
    """
    model = Tag


class ProtectSystemUserGroupMixin(object):
    """
    システム管理のユーザグループを保護する Mixin
    """
    def render_to_response(self, *args, **kwargs):
        """
        システム管理オブジェクトのとき404
        """
        if not self.object.auto_created:
            return super().render_to_response(*args, **kwargs)
        else:
            raise Http404


class UserGroupUpdateView(
    ProtectSystemUserGroupMixin, ActiveObjectUpdateViewSuper):
    """
    ユーザグループの編集

    アクセス制御 :
      指定された pk でユーザグループが存在しないとき 404
      ユーザグループがアクティブでないとき 404
      認証されていないときログイン要求
      管理者でないときエラー
      ユーザグループがシステム管理のとき 404
    """
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('admin_usergroups')

    def form_valid(self, form):
        # 変更されたフィールドを取得
        changed = form.changed_data
        response = super().form_valid(form)

        # 参加者が変更されたとき整合性を保証
        if 'users' in changed:
            self.object.changed_users()

        return response


class UserGroupDeleteView(ProtectSystemUserGroupMixin, DeactivateViewSuper):
    """
    ユーザグループの無効化

    アクセス制御 :
      指定された pk でユーザグループが存在しないとき 404
      ユーザグループがアクティブでないとき 404
      認証されていないときログイン要求
      管理者でないときエラー
      ユーザグループがシステム管理のとき 404
    """
    model = UserGroup
    success_url = reverse_lazy('admin_usergroups')
