from django.db import models
from django.db.models.query import Q
from django.contrib.auth.models import AbstractUser

from todo.models import Tag, Task


class MyUser(AbstractUser):
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return '{} {}'.format(self.last_name, self.first_name)

    def own_groups(self):
        """
        所属するユーザグループのうち有効なものを返す
        """
        return self.usergroup_set.filter(is_active=True)

    def usable_private_tags(self):
        """
        使用可能な非共有タグを返す
        """
        # 自分がアクセス可能なタグが含まれる可能性のあるタスクは,
        # 有効なタスク(Task.active_django_objects)のうち,
        # public なタスクか,
        # 自身が所属するグループが対象に含まれるタスク
        # (タグを取り出すためにタグが登録されていないものは除く)
        tasks = Task.active_django_objects().filter(
            Q(public=True) |
            Q(users__in=self.own_groups(), tags__isnull=False)).distinct()

        # 自分がアクセス可能なタグが含まれる可能性のあるタスクに
        # 登録されたすべてのタグの pk
        tasks_tags_pk = tasks.values_list('tags__pk', flat=True).distinct()

        # 使用可能な非共有タグは, 有効な非共有タグのうち,
        # 自分が対象のタスクに登録されたタグか,
        # 公開タスクに登録された非共有タグ,
        # または自分が作成したタグ
        return Tag.objects.filter(public=False, is_active=True).filter(
            Q(pk__in=tasks_tags_pk) | Q(owner=self))

    def usable_tags(self):
        """
        使用可能なすべてのタグを返す
        """
        # 使用可能なタグは, 有効なタグのうち,
        # 共有タグか, 使用可能な非共有タグ
        return Tag.objects.filter(is_active=True).filter(
            Q(public=True) | Q(pk__in=self.usable_private_tags()))

    def deactivate(self):
        self.is_active = False
        self.save()

        for tag in self.tag_set.all():
            tag.deactivate()

        for group in self.own_groups():
            group.users.remove(self)
            if group.users.all():
                group.changed_users()
            else:
                group.deactivate()
