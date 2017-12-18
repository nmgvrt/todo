import json
import calendar
import datetime

from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.db.models.query import Q
from django.db.models import Min, Max
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from app.decorators import *

from .forms import *
from .models import *
from .decorators import *


def can_manage_tag(user, *args, **kwargs):
    try:
        tag = Tag.objects.get(pk=kwargs['pk'])
    except:
        return False

    if tag.public:
        if not user.is_superuser:
            return False
    else:
        if tag.owner != user:
            return False

    return True


def delete_view_func(request, obj, redirect_to=None):
    """
    オブジェクトを削除(無効化)する関数ビュー
    """
    cls_lower = obj.__class__.__name__.lower()

    if request.POST:
        obj.deactivate()
        redirect_to = redirect_to or 'admin_{}s'.format(cls_lower)

        return redirect(reverse(redirect_to))

    return render(request, 'todo/delete_{}.html'.format(
        cls_lower), {'object': obj})


def redirect_task_list(pk):
    """
    公開タスクなら公開タスク一覧,
    非公開タスクなら非公開タスク一覧 へリダイレクト
    """
    if Task.objects.get(pk=pk).is_public():
        return redirect(reverse('public_tasks'))
    else:
        return redirect(reverse('my_tasks'))


def error(request):
    """
    エラーページ

    アクセス制御 :
      エラー発生時以外のアクセスでトップページへリダイレクト
    """
    msgs = request._messages._get()[0]
    if not msgs:
        return redirect(reverse('index'))

    return render(request, 'todo/error.html')


@login_required
def mypage(request):
    """
    マイページ
    締め切りが settings.RECENT 日後までの自分の未完了タスクを表示
    """
    end = timezone.now() + datetime.timedelta(days=settings.RECENT)

    recent_tasks = Task.active_objects().filter(
        done=False, deadline__lte=end, closest__users__users=request.user
    ).distinct().order_by('deadline', 'tree_id', 'lft')

    return render(request, 'todo/mypage.html', {
        'object_list': recent_tasks, 'recent': settings.RECENT})


def get_datetime(year, month, start=True):
    """
    指定された月の最初 ($y / $m / 0 00:00:00)
    または最後 ($y / $m / [28, 29, 30, 31] 23:59:59) の datetime を返す
    """
    base = [year, month]
    if start:
        base += [1, 0, 0, 0]
    else:
        base += [calendar.monthrange(year, month)[1], 23, 59, 59]

    return timezone.make_aware(datetime.datetime(*base))


class CalendarPaginator(object):
    """
    カレンダー用のペジネータ
    """
    max_year = 2199

    def __init__(self, year, month, start, end):
        self.year = year
        self.month = month
        self.start = start
        self.end = end
        self.ready = False

    def validate_year_month(self, *args):
        """
        与えられた年・月が有効かどうかを判定する
        問題があるとき例外を投げる
        """
        year, month = map(int, args)

        if month < 1 or month > 12:
            raise Exception('存在しない月が指定されました.')

        # 指定された年・月の最初
        arg_start = get_datetime(year, month)
        # 指定された年・月の最後
        arg_end = get_datetime(year, month, start=False)

        # 指定された年・月がカレンダーの開始よりも早いとき
        if arg_start < self.start:
            raise Exception('{}には該当するタスクがありません.'.format(
                '{}年{}月'.format(arg_start.year, arg_start.month)))

        # 指定された年が制限値 (self.max_year) を超えたとき
        if arg_end.year > self.max_year:
            raise Exception('{} 年以降は非対応です.'.format(self.max_year + 1))
        elif arg_end > self.end:
            raise Exception('{}には該当するタスクがありません.'.format(
                '{}年{}月'.format(arg_end.year, arg_end.month)))

        if not self.ready:
            self.year = year
            self.month = month
            self.ready = True

        return year, month

    def add_delta(self, delta=1):
        """
        次の月または前の月を取得
        """
        year = self.year
        month = self.month + delta
        if month < 1:
            year -= 1
            month = 12
        if month > 12:
            year += 1
            month = 1

        return year, month

    def _can_move(self, delta=1):
        """
        次の月または前の月があるとき True
        そうでなければ False
        """
        added = self.add_delta(delta=delta)
        try:
            self.validate_year_month(*added)
        except:
            return False

        return True

    def previous_unsafe(self):
        return self.add_delta(delta=-1)

    def previous_year(self):
        return self.previous_unsafe()[0]

    def previous_month(self):
        return self.previous_unsafe()[1]

    def has_previous(self):
        return self._can_move(delta=-1)

    def next_unsafe(self):
        return self.add_delta()

    def next_year(self):
        return self.next_unsafe()[0]

    def next_month(self):
        return self.next_unsafe()[1]

    def has_next(self):
        return self._can_move()


def calendar_view_func(request, year=None, month=None):
    """
    カレンダーを表示するビューを返す
    """
    # 未完了の自分のタスクを取得
    tasks = Task.active_objects().filter(
        done=False, closest__users__users=request.user).distinct()
    today = timezone.localtime(timezone.now())

    if tasks:
        # カレンダーの開始は自分の未完了タスクの一番早い締め切りの月の最初
        a = timezone.localtime(tasks.aggregate(
            Min('deadline'))['deadline__min']).replace(
                day=1, hour=0, minute=0, second=0)
        # カレンダーの終了は自分の未完了タスクの一番遅い締め切りの月の最後
        b = timezone.localtime(
            tasks.aggregate(Max('deadline'))['deadline__max'])
        b = b.replace(day=calendar.monthrange(
            b.year, b.month)[1], hour=23, minute=59, second=59)

        # 年・月は引数で与えられるかカレンダーの最初
        year = year or a.year
        month = month or a.month

        # ペジネータのインスタンスを生成
        paginator = CalendarPaginator(year, month, a, b)

        # 与えられた年・月を検査
        try:
            year, month = paginator.validate_year_month(year, month)
        except Exception as e:
            return raise_error(request, e)

        # 指定された年・月のタスクに限定
        start = get_datetime(year, month)
        end = get_datetime(year, month, start=False)
        tasks = tasks.filter(deadline__gte=start, deadline__lte=end)
    else:
        # 該当するタスクがひとつもないとき今月のカレンダーを表示
        year = today.year
        month = today.month
        a = get_datetime(year, month)
        b = get_datetime(year, month, start=False)
        paginator = CalendarPaginator(year, month, a, b)

    # データを整形
    task_map = {}
    for task in tasks:
        local = timezone.localtime(task.deadline)
        if local.day not in task_map:
            task_map[local.day] = []
        task_map[local.day].append(task)

    raw_calendar = calendar.Calendar(
        firstweekday=6).monthdays2calendar(year, month)
    task_calendar = []
    for raw_row in raw_calendar:
        row = []
        for day, weekday in raw_row:
            row.append({
                'day': day,
                'weekday': weekday,
                'tasks': task_map[day] if day in task_map else []
            })
        task_calendar.append(row)

    return render(request, 'todo/calendar.html', {
        'calendar': task_calendar, 'paginator': paginator,
        'today': today, 'tasks': tasks})


@login_required
def earliest_month_calendar_view(request):
    """
    最も締め切りが早いタスクが存在する月のカレンダーを表示
    """
    return calendar_view_func(request)


@login_required
def calendar_view(request, year, month):
    """
    指定された月のカレンダーを表示
    """
    return calendar_view_func(request, year=year, month=month)


@login_required
def add_task(request):
    """
    親タスクの作成
    オブジェクトの生成は RootTaskForm が管理

    アクセス制御 :
      認証されていないときログイン要求
    """
    # 初期値
    # 優先度 : 標準, 繰り返し : なし,
    # 公開 : True, 締め切り : 現在
    initial = {
        'priority': 0,
        'repeat': 0,
        'public': True,
        'deadline': timezone.now(),
    }

    form = RootTaskForm(user=request.user, initial=initial)

    if request.POST:
        form = RootTaskForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            form.instance.created_callback()

            return redirect_task_list(form.instance.pk)

    return render(request, 'todo/add_task.html', {'form': form})


@raise_404_if_not_exists(Task)
@raise_404_if_deleted(Task)
@login_required
@can_manage_object(test_can_manage_task)
@can_change_task()
@can_insert_child_task()
def add_child_task(request, pk):
    """
    子タスクの作成
    オブジェクトの生成は ChildTaskForm が管理

    アクセス制御 :
      指定された pk でタスクが存在しないとき 404
      タスクがアクティブでないとき 404
      認証されていないときログイン要求
      タスクへアクセスする権限がないときエラー
      タスクが変更不可(完了済)のときエラー
      タスクが制限高さに到達したときエラー
    """
    parent = get_object_or_404(Task, pk=pk)

    # 初期値 - 締め切り : 親タスクの締め切り
    initial = {'deadline': parent.deadline}

    form = ChildTaskForm(user=request.user, task=parent, initial=initial)

    if request.POST:
        form = ChildTaskForm(request.POST, user=request.user, task=parent)

        if form.is_valid():
            # 子タスクに親タスクを指定
            form.instance.parent = parent
            form.save()
            form.instance.created_callback()

            return redirect_task_list(pk)

    return render(
        request, 'todo/add_child_task.html', {'task': parent, 'form': form})


@raise_404_if_not_exists(Task)
@raise_404_if_deleted(Task)
@login_required
@can_manage_object(test_can_manage_task)
@can_change_task()
def edit_task(request, pk):
    """
    タスクの編集
    オブジェクトの編集は RootTaskForm か ChildTaskForm が管理

    アクセス制御 :
      指定された pk でタスクが存在しないとき 404
      タスクがアクティブでないとき 404
      認証されていないときログイン要求
      タスクへアクセスする権限がないときエラー
      タスクが変更不可(完了済)のときエラー
    """
    task = get_object_or_404(Task, pk=pk)

    # ルートタスクかどうかでフォームクラスとテンプレートを分岐
    if task.is_root_node():
        form_cls = RootTaskForm
        template = 'todo/edit_root_task.html'
    else:
        form_cls = EditChildTaskForm
        template = 'todo/edit_child_task.html'

    form = form_cls(user=request.user, task=task, instance=task)

    if request.POST:
        form = form_cls(
            request.POST, user=request.user, task=task, instance=task)
        if form.is_valid():
            changed = form.changed_data
            form.save()
            # 対象者が変更されたとき
            if 'users' in changed:
                # タスクの対象者が変更されたときの整合性を保証
                task.changed_users()

            return redirect_task_list(pk)

    return render(request, template, {'task': task, 'form': form})


@raise_404_if_not_exists(Task)
@raise_404_if_deleted(Task)
@login_required
@can_manage_object(test_can_manage_task)
@can_change_task()
def delete_task(request, pk):
    """
    タスクの削除

    アクセス制御 :
      指定された pk でタスクが存在しないとき 404
      タスクがアクティブでないとき 404
      認証されていないときログイン要求
      タスクへアクセスする権限がないときエラー
      タスクが変更不可(完了済)のときエラー
    """
    task = get_object_or_404(Task, pk=pk)
    redirect_to = 'public_tasks' if task.is_public() else 'my_tasks'

    return delete_view_func(request, task, redirect_to=redirect_to)


@raise_404_if_not_exists(Task)
@raise_404_if_deleted(Task)
@login_required
@can_manage_object(test_can_manage_task)
@can_change_task()
def finish_task(request, pk):
    """
    タスクの完了者の登録
    オブジェクトの完了は FinishTaskForm が管理

    アクセス制御 :
      指定された pk でタスクが存在しないとき 404
      タスクがアクティブでないとき 404
      認証されていないときログイン要求
      タスクへアクセスする権限がないときエラー
      タスクが変更不可(完了済)のときエラー
    """
    task = get_object_or_404(Task, pk=pk)

    form = FinishTaskForm(task=task, instance=task)

    if request.POST:
        form = FinishTaskForm(request.POST, task=task, instance=task)
        if form.is_valid():
            form.save()
            # タスクが完了していないか確認
            task.check_state()

            return redirect_task_list(pk)

    return render(request, 'todo/finish_task.html', {
        'task': task, 'form': form})


@raise_404_if_not_exists(Task)
@raise_404_if_deleted(Task)
@login_required
@can_manage_object(test_can_manage_task)
@can_change_task()
def change_my_state(request, pk):
    """
    自分が対象のタスクで自身を完了に変更する

    アクセス制御 :
      指定された pk でタスクが存在しないとき 404
      タスクがアクティブでないとき 404
      認証されていないときログイン要求
      タスクへアクセスする権限がないときエラー
      タスクが変更不可(完了済)のときエラー
      すでに自身がタスクを完了しているときエラー
      タスクの対象者に含まれないときエラー
    """
    task = get_object_or_404(Task, pk=pk)

    if request.user in task.done_users.all():
        return raise_error(request, 'あなたはすでにこのタスクを完了しています.')

    if request.user not in task.unique_users():
        return raise_error(request, 'あなたはこのタスクの対象者ではありません.')

    if request.POST:
        # 自分をタスクの完了者に追加
        task.done_users.add(request.user)
        # タスクが完了していないか確認
        task.check_state()

        return redirect_task_list(pk)

    return render(request, 'todo/change_my_state.html', {'task': task})


def usergroup_response(usergroups, is_group=True):
    """
    UserGroup の Queryset を json にしたレスポンスを返す
    """
    l = []
    for group in usergroups:
        dic = {'pk': group.pk}
        dic['display'] = group.name if is_group else group.users.first(
            ).get_full_name()
        l.append(dic)

    return HttpResponse(json.dumps(l), content_type='application/json')


@user_passes_test_404(is_authenticated)
def json_usergroup_user(request):
    """
    ルートタスクに登録可能なユーザ
    (実装上は参加者が 1 人の UserGroup)の json を返す

    アクセス制御:
      認証されていないとき 404
    """
    # ルートタスクに登録可能なユーザは, 有効なユーザのうち,
    # 自動生成された(自動生成されるのは参加者が 1 人のものだけ) UserGroup
    return usergroup_response(UserGroup.objects.filter(
        auto_created=True, is_active=True), is_group=False)


@user_passes_test_404(is_authenticated)
def json_usergroup_group(request):
    """
    ルートタスクに登録可能なグループの json を返す

    アクセス制御:
      認証されていないとき 404
    """
    # ルートタスクに登録可能なグループは, 有効なグループのうち,
    # 自動生成されていない UserGroup
    return usergroup_response(
        UserGroup.objects.filter(auto_created=False, is_active=True))


@user_passes_test_404(is_authenticated)
@raise_404_if_not_exists(Task)
@raise_404_if_deleted(Task)
@user_passes_test_404(test_can_manage_task)
def json_usergroup_user_child(request, pk):
    """
    子タスクに登録可能なユーザ
    (実装上は参加者が 1 人の UserGroup)の json を返す

    アクセス制御:
      認証されていないとき 404
      タスクがアクティブでないとき 404
      タスクへアクセスする権限がないとき404
      指定された pk でタスクが存在しないとき 404
    """
    parent = get_object_or_404(Task, pk=pk)

    # 子タスクに登録可能なユーザは closest なノードの対象者
    return usergroup_response(UserGroup.objects.filter(
        users__pk__in=parent.closest_node().unique_users(),
        auto_created=True).distinct(), is_group=False)


@user_passes_test_404(is_authenticated)
@raise_404_if_not_exists(Task)
@raise_404_if_deleted(Task)
@user_passes_test_404(test_can_manage_task)
def json_usergroup_group_child(request, pk):
    """
    子タスクに登録可能なグループの json を返す

    アクセス制御:
      認証されていないとき 404
      タスクがアクティブでないとき 404
      タスクへアクセスする権限がないとき404
      指定された pk でタスクが存在しないとき 404
    """
    parent = get_object_or_404(Task, pk=pk)

    # 子タスクに登録可能なグループは closest なノードのグループ
    return usergroup_response(
        parent.closest_node().users.filter(auto_created=False))


@user_passes_test_404(is_authenticated)
@raise_404_if_not_exists(Task)
@raise_404_if_deleted(Task)
@user_passes_test_404(test_can_manage_task)
def json_usergroup_user_child_edit(request, pk):
    """
    子タスク編集時に登録可能なユーザ
    (実装上は参加者が 1 人の UserGroup)の json を返す

    アクセス制御:
      認証されていないとき 404
      タスクがアクティブでないとき 404
      タスクへアクセスする権限がないとき404
      指定された pk でタスクが存在しないとき 404
    """
    task = get_object_or_404(Task, pk=pk)

    # 子タスク編集時に登録可能なユーザは親タスクの closest なノードの対象者
    return usergroup_response(UserGroup.objects.filter(
        users__pk__in=task.get_parent().closest_node().unique_users(),
        auto_created=True).distinct(), is_group=False)


@user_passes_test_404(is_authenticated)
@raise_404_if_not_exists(Task)
@raise_404_if_deleted(Task)
@user_passes_test_404(test_can_manage_task)
def json_usergroup_group_child_edit(request, pk):
    """
    子タスク編集時に登録可能なグループの json を返す

    アクセス制御:
      認証されていないとき 404
      タスクがアクティブでないとき 404
      タスクへアクセスする権限がないとき404
      指定された pk でタスクが存在しないとき 404
    """
    task = get_object_or_404(Task, pk=pk)

    # 子タスク編集時に登録可能なグループは親タスクの closest なノードのグループ
    return usergroup_response(
        task.get_parent().closest_node().users.filter(auto_created=False))


def tag_response(tags):
    """
    Tag の Queryset を json にしたレスポンスを返す
    """
    l = []
    for tag in tags:
        l.append({
            'display': tag.name,
            'pk': tag.pk,
            'color': tag.css_color(),
        })

    return HttpResponse(json.dumps(l), content_type='application/json')


@user_passes_test_404(is_authenticated)
def json_tag_public(request):
    """
    ルートタスクに登録可能な共有タグの json を返す

    アクセス制御:
      認証されていないとき 404
    """
    # ルートタスクに登録可能な共有タグは, 有効で public なタグ
    return tag_response(Tag.objects.filter(public=True, is_active=True))


@user_passes_test_404(is_authenticated)
def json_tag_private(request):
    """
    ルートタスクに登録可能な非共有タグの json を返す

    アクセス制御:
      認証されていないとき 404
    """
    # ルートタスクに登録可能な非共有タグは,
    # ユーザが使用可能な非共有タグ(MyUser.usable_private_tags)
    return tag_response(request.user.usable_private_tags())
