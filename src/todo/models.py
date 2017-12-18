import calendar
import datetime

from django.apps import apps
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.query import Q
from django.db.models import Min, Max
from django.db.models.signals import post_save

from mptt.models import MPTTModel, TreeForeignKey

from cauth.utils import UserCls

__all__ = [
    'get_current_year', 'Color', 'Tag', 'UserGroup', 'Task',
]


def get_current_year():
    now = timezone.localtime(timezone.now())
    start_year = now.year if now.month > 3 else now.year - 1

    start = datetime.datetime(
        start_year, 4, 1, 0, 0, 0, tzinfo=now.tzinfo)
    end = datetime.datetime(start_year + 1, 3, calendar.monthrange(
        start_year + 1, 3)[1], 0, 0, 0, tzinfo=now.tzinfo)

    return start, end


class Active(models.Model):
    is_active = models.BooleanField('有効', default=True)

    class Meta:
        abstract = True

    def deactivate(self):
        self.is_active = False
        self.save()


class Color(Active):
    r = models.PositiveIntegerField('R')
    g = models.PositiveIntegerField('G')
    b = models.PositiveIntegerField('B')

    class Meta:
        verbose_name = verbose_name_plural = '色'

    def __str__(self):
        return 'rgb({}, {}, {})'.format(
            self.r, self.g, self.b)


class Tag(Active):
    name = models.CharField('タグ名', max_length=32)
    color = models.ForeignKey(Color, verbose_name='タグ色')
    public = models.BooleanField('公開', default=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, verbose_name='登録者')

    class Meta:
        verbose_name = verbose_name_plural = 'タグ'

    def __str__(self):
        return 'タグ : {}'.format(self.name)

    def css_color(self):
        return str(self.color)

    def deactivate(self):
        super().deactivate()

        for task in self.task_set.filter(done=False):
            task.tags.remove(self)


class UserGroup(Active):
    name = models.CharField('グループ名', max_length=64)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, verbose_name='ユーザ')
    auto_created = models.BooleanField('システム管理オブジェクト', default=False)

    class Meta:
        verbose_name = verbose_name_plural = 'ユーザグループ'

    def __str__(self):
        return 'ユーザグループ : {}'.format(self.get_displayname())

    def get_displayname(self):
        if self.auto_created:
            return self.users.all().first()
        else:
            return self.name

    def flat_members(self):
        names = [user.get_full_name() for user in self.users.all()]

        return ', '.join(names)

    def ongoing_task_set(self):
        return self.task_set.filter(
            pk__in=Task.active_objects().filter(done=False)).order_by('-level')

    def changed_users(self):
        for root in self.ongoing_task_set().filter(level=0):
            root.changed_users()

    def deactivate(self):
        super().deactivate()

        for task in self.ongoing_task_set():
            task.users.remove(self)
            if task.is_root_node():
                task.changed_users()


class CustomMPTTModel(MPTTModel, Active):
    class Meta(MPTTModel.Meta):
        abstract = True

    def _wrap(self, func_name, *args, only_active=True, **kwargs):
        nodes = getattr(super(), func_name)(*args, **kwargs)
        if only_active:
            nodes = nodes.filter(is_active=True)

        return nodes

    def get_family(self, *args, only_active=True, **kwargs):
        return self._wrap(
            'get_family', *args, only_active=only_active, **kwargs)

    def get_ancestors(self, *args, only_active=True, **kwargs):
        return self._wrap(
            'get_ancestors', *args, only_active=only_active, **kwargs)

    def get_descendants(self, *args, only_active=True, **kwargs):
        return self._wrap(
            'get_descendants', *args, only_active=only_active, **kwargs)

    def get_descendants_include_self(self, *args, only_active=True, **kwargs):
        kwargs['include_self'] = True

        return self._wrap(
            'get_descendants', *args, only_active=only_active, **kwargs)


class Task(CustomMPTTModel):
    django_objects = models.Manager()

    inherited_fields = [
        'name', 'description', 'priority', 'repeat', 'public'
    ]
    inherited_m2m_fields = [
        'users', 'tags'
    ]

    PRIORITY_CHOICES = (
        (0, '標準'),
        (1, '重要'),
        (2, '緊急'),
    )

    REPEAT_TYPE_CHOICES = (
        (0, '繰り返しなし'),
        (1, '毎週'),
        (2, '毎月'),
    )

    name = models.CharField('タスク名', max_length=256)
    description = models.TextField(
        '説明', blank=True, help_text='タスクに関する説明を追加する場合は入力してください.')
    created = models.DateTimeField('作成日時', auto_now_add=True)
    deadline = models.DateTimeField('締め切り')
    earliest = models.DateTimeField('直近の締め切り', null=True, blank=True)
    latest = models.DateTimeField('完了予定日', null=True, blank=True)
    priority = models.PositiveIntegerField(
        '優先度', choices=PRIORITY_CHOICES, default=0)
    repeat = models.PositiveIntegerField(
        '繰り返し', choices=REPEAT_TYPE_CHOICES, default=0)
    done = models.BooleanField('完了', default=False)
    public = models.BooleanField(
        '公開', default=True, help_text='公開タスクは全体に公開され, だれでも編集できます.')

    parent = TreeForeignKey(
        'self', null=True, blank=True,
        verbose_name='親タスク', related_name='childen')
    root = TreeForeignKey(
        'self', null=True, blank=True,
        verbose_name='ルートタスク', related_name='rev_root')
    closest = TreeForeignKey(
        'self', null=True, blank=True,
        verbose_name='Closest', related_name='rev_closest')
    tags = models.ManyToManyField(
        Tag, blank=True, verbose_name='タグ',
        help_text="""
            <p>タスクにタグを付けて管理できます. 子孫にも継承されます. </p>
            <p>非共有タグをタスクに登録した場合, 該当タスクにアクセス可能なユーザ全員に共有されます.</p>
        """)
    users = models.ManyToManyField(
        UserGroup, blank=True, verbose_name='対象ユーザ(グループ)',
        help_text='ユーザとグループを組み合わせて複数指定できます. ルートタスク以外では省略できます.')
    done_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        verbose_name='完了したユーザ', related_name='all_finished_task')

    class Meta:
        verbose_name = verbose_name_plural = 'タスク'

    class MPTTMeta:
        order_insertion_by = ['deadline']

    @classmethod
    def active_objects(cls):
        start, _ = get_current_year()

        return cls.objects.filter(is_active=True).filter(
            Q(done=False) | Q(done=True, root__latest__gt=start))

    @classmethod
    def active_django_objects(cls):
        start, _ = get_current_year()

        return cls.django_objects.filter(is_active=True).filter(
            Q(done=False) | Q(done=True, root__latest__gt=start))

    def __str__(self):
        return 'タスク : {}'.format(self.name)

    def get_tree(self):
        """
        タスクが含まれる木を返す
        """
        return self.active_objects().filter(tree_id=self.tree_id)

    def is_out_of_date(self):
        """
        タスクの締め切りを過ぎたかどうかを返す
        """
        return self.deadline < timezone.now()

    def get_priority(self):
        """
        タスクの優先度を返す
        """
        return self.priority or self.get_root().priority

    def is_repeat(self):
        """
        タスクが繰り返しかどうかを返す
        """
        return True if self.get_root().repeat else False

    def is_public(self):
        """
        タスクが公開されているかどうかを返す
        """
        return self.get_root().public

    def get_parent(self):
        """
        タスクの親を返す (ただしルートなら自身)
        """
        return self.parent or self

    def display_groups(self):
        """
        タスクに設定されたグループ名をカンマ区切りで連結して返す
        """
        return ', '.join(self.get_users().filter(
            auto_created=False).values_list('name', flat=True))

    def reach_max_depth(self):
        """
        制限高さに到達したかどうかを返す
        (ウェブページのレイアウト上の制約で 6 段までに設定)
        """
        return self.level >= 5

    def unique_tags(self):
        """
        タスクのタグを返す
        """
        return self.get_root().tags.all()

    def get_users(self):
        """
        タスクの対象者(グループ)を返す
        """
        # タスクに対象者が設定されていれば優先
        # そうでなければルートタスクの対象者
        # return self.users.all() or self.root.users.all()

        # タスクの対象者は closest なノードの対象者
        return self.closest_node().users.all()

    def unique_users(self):
        """
        タスクの対象者を MyUser の Queryset で返す
        """
        groups = self.get_users()
        # すべての対象者は,
        # タスクに紐付けられた UserGroup のすべての参加者
        unique_users_pk = groups.distinct(
            ).values_list('users__pk', flat=True)

        # すべての対象者を返す
        return UserCls().objects.filter(pk__in=unique_users_pk)


    def created_callback(self):
        """
        タスクの作成時に検索用フィールドの整合性を保証
        """
        self.root = self.get_root()
        self.closest = self.closest_node()
        self.save()

    def closest_node(self):
        """
        対象者を指定してある最も近いノードを返す
        """
        # 自身を含む有効な祖先のうち対象者が null でないものについて,
        # 深さの深いものから並べる
        # (未完了のタスクでのみ
        # 無効な対象者が users に登録されていないことが保証される)
        self = Task.objects.get(pk=self.pk)
        upper = self.get_ancestors(include_self=True).filter(
            users__isnull=False).order_by('-level')

        return upper.first() if upper else self.get_root()

    def selectable_usergroups(self):
        """
        子タスクの追加時に対象者に選択可能なすべての UserGroup を返す
        """
        # 対象者を指定してある最も近いノード
        closest = self.closest_node()

        # 選択可能な UserGroup は,
        # closest の Task.unique_users のユーザ(グループ)か,
        # closest の グループ
        return UserGroup.objects.filter(
            Q(users__pk__in=closest.unique_users(), auto_created=True) |
            Q(pk__in=closest.users.all())).distinct()

    def set_range(self):
        """
        タスクの完了時にルートタスクのソート用締め切り日時の整合性を保証する
        """
        self = Task.objects.get(pk=self.pk)
        # tasks = Task.objects.filter(tree_id=self.tree_id)
        # ツリーのすべてのタスク
        tasks = self.get_family()
        # タスクが進行中のとき未完了のタスクに限定
        if self.level != 0:
            tasks = tasks.filter(done=False)

        vals = tasks.aggregate(Min('deadline'), Max('deadline'))
        root = self.get_root()
        root.earliest = vals['deadline__min']
        root.latest = vals['deadline__max']
        root.save()

    def set_finished(self):
        """
        タスクを完了にする
        """
        # タスクが未完了のとき
        if not self.done:
            # タスクの完了者はタスクの対象者
            self.done_users = self.unique_users()
            self.done = True
            self.save()

    def set_ongoing(self):
        """
        タスクを未完了にする
        """
        # タスクが完了しているとき
        if self.done:
            self.done = False
            self.save()

    def check_state(self):
        """
        タスクの状態(完了/未完了)が変更されていないか確認
        """
        # すべての対象者の集合
        all_users = set(list(self.unique_users().values_list('pk', flat=True)))
        # すべての完了したユーザの集合
        done_users = set(list(self.done_users.values_list('pk', flat=True)))

        changed_state = False
        # 対象者の集合が完了者の集合の部分集合のとき
        # (すべての対象者が完了したユーザの集合に含まれる = 完了)
        if all_users.issubset(done_users):
            # 完了しているはずが未完了のとき
            if not self.done:
                # 自身以下のタスクを完了する
                for node in self.get_descendants(include_self=True):
                    node.set_finished()
                changed_state = True

                # ルートタスクの完了時に繰り返しが設定されている場合
                if self.is_root_node() and self.repeat != 0:
                    # ツリーを複製
                    self.clone_tree()
        else:
            # 未完了のはずが完了しているとき
            if self.done:
                # 自身を未完了にする
                self.set_ongoing()
                changed_state = True

        # 状態に変更があるタスクがある場合
        if changed_state:
            # ルートタスクソート用の締め切り日時を更新
            self.set_range()

    def clean_users(self):
        """
        関連オブジェクトの変更によってタスクの対象者が変更されたとき,
        選択できないはずの対象者が設定されていたら除外
        """
        # ルートタスクのとき(ルートタスクは誰でも良い)
        if not self.is_root_node():
            # 対象者を指定してあるとき
            if self.users.all():
                # 親タスクを取得
                # (ルートの時は parent が None)になるため self
                parent = self.parent or self
                # 自身の対象者に自身に設定可能な対象者
                # (親タスクの Task.selectable_usergroups)以外が含まれるとき除外
                self.users.remove(*self.users.exclude(
                    pk__in=parent.selectable_usergroups()))

            # Closest の整合性を保証
            closest = self.closest_node()
            if self.closest != closest:
                self.closest = closest
                self.save()

    def changed_users(self):
        """
        タスクの対象者の変更時に,
        タスクツリーの自身以下の整合性を保証する
        """
        # 自身以下のタスクすべてについて深さが浅いものから順に
        for task in self.get_descendants(include_self=True).order_by('level'):
            # 選択不可な対象者が含まれる場合に除外
            task.clean_users()
            # 対象者の変更でタスクが完了していないか確認
            # (または完了していたものが未完了になっていないか)
            task.check_state()

    def _next_deadline(self, avoid_holiday=True):
        """
        繰り返し種類に応じた次の締め切りを返す
        """
        if self.get_root().repeat == 1:
            # 週ごとの繰り返し
            # 7 日後を次の締め切り
            next_deadline = self.deadline + datetime.timedelta(days=7)
        else:
            # 月ごとの繰り返し
            # 翌月同日を次の締め切り

            # [year, month, day, hour, minute, second]
            list_time = list(timezone.localtime(
                self.deadline).timetuple())
            # 月 + 1
            list_time[1] += 1
            # 翌月の最終日
            last_day_of_month = calendar.monthrange(*list_time[:2])[1]
            # もし存在しない日なら
            if list_time[2] > last_day_of_month:
                list_time[2] = last_day_of_month

            next_deadline = datetime.datetime(
                *list_time[:6], tzinfo=timezone.get_current_timezone())

            # 土日をさけるなら
            if avoid_holiday:
                # 曜日を取得
                weekday = calendar.weekday(*list_time[:3])
                # 土日なら
                if weekday > 4:
                    # 直前の金曜日
                    next_deadline += datetime.timedelta(
                        days=-(weekday - 4))

        return next_deadline

    def clone_tree(self):
        """
        ツリーを複製
        """

        # 深さの浅いものから順にツリーのすべてのノードを取得
        # family = Task.django_objects.filter(
        #     tree_id=self.tree_id).order_by('level')
        family = self.get_family().order_by('level')

        # 複製元のタスクの pk と
        # 新たに追加したタスクの pk を対応づける辞書
        pk_map = {None: None}

        # ツリーのすべてのタスクについて
        for node in family:
            # 親があれば pk を取得
            parent = None if node.parent is None else node.parent.pk

            new = {}
            # タスクの複製に必要な情報を取り出す
            for key in self.inherited_fields:
                new[key] = getattr(node, key)
            # 新たに設定する情報を追加する
            new.update({
                # 繰り返し種類に応じて新たな締め切りを取得
                'deadline': node._next_deadline(),
                # 新たな親を指定
                'parent': pk_map[parent]
            })
            # 新たなタスクを作成
            new_task = Task.objects.create(**new)
            # ManyToMany なフィールドの情報を複製
            for key in self.inherited_m2m_fields:
                getattr(new_task, key).add(*getattr(node, key).all())

            new_task.created_callback()

            # 自身を親とするタスクのために辞書に登録
            pk_map[node.pk] = new_task

    def deactivate(self):
        """
        タスクを削除(無効化)する
        """
        Task.django_objects.filter(pk__in=self.get_descendants(
            include_self=True)).update(is_active=False)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def saved_user_callback(sender, instance, created, **kwargs):
    # ユーザの作成時のみ
    if created:
        # ユーザ 1 人の UserGroup を作成
        group = UserGroup.objects.create(
            name='auto_{}'.format(instance.pk), auto_created=True)
        group.users.add(instance)


@receiver(post_save, sender=Task)
def saved_task_callback(sender, instance, created, **kwargs):
    # タスクが保存されたときに
    # 必要に応じてルートタスクのソート用の締め切り日時を更新
    instance = sender.objects.get(pk=instance.pk)
    root = instance.get_root()
    if not instance.done:
        earliest = root.earliest
        set_earliest = earliest is None or instance.deadline < earliest
        if set_earliest:
            root.earliest = instance.deadline

        latest = root.latest
        set_latest = latest is None or instance.deadline > latest
        if set_latest:
            root.latest = instance.deadline

        if set_earliest or set_latest:
            root.save()
