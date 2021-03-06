# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-18 05:28
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('r', models.PositiveIntegerField(verbose_name='R')),
                ('g', models.PositiveIntegerField(verbose_name='G')),
                ('b', models.PositiveIntegerField(verbose_name='B')),
            ],
            options={
                'verbose_name': '色',
                'verbose_name_plural': '色',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('name', models.CharField(max_length=32, verbose_name='タグ名')),
                ('public', models.BooleanField(default=True, verbose_name='公開')),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='todo.Color', verbose_name='タグ色')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='登録者')),
            ],
            options={
                'verbose_name': 'タグ',
                'verbose_name_plural': 'タグ',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('name', models.CharField(max_length=256, verbose_name='タスク名')),
                ('description', models.TextField(blank=True, help_text='タスクに関する説明を追加する場合は入力してください.', verbose_name='説明')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('deadline', models.DateTimeField(verbose_name='締め切り')),
                ('earliest', models.DateTimeField(blank=True, null=True, verbose_name='直近の締め切り')),
                ('latest', models.DateTimeField(blank=True, null=True, verbose_name='完了予定日')),
                ('priority', models.PositiveIntegerField(choices=[(0, '標準'), (1, '重要'), (2, '緊急')], default=0, verbose_name='優先度')),
                ('repeat', models.PositiveIntegerField(choices=[(0, '繰り返しなし'), (1, '毎週'), (2, '毎月')], default=0, verbose_name='繰り返し')),
                ('done', models.BooleanField(default=False, verbose_name='完了')),
                ('public', models.BooleanField(default=True, help_text='公開タスクは全体に公開され, だれでも編集できます.', verbose_name='公開')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('closest', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rev_closest', to='todo.Task', verbose_name='Closest')),
                ('done_users', models.ManyToManyField(blank=True, related_name='all_finished_task', to=settings.AUTH_USER_MODEL, verbose_name='完了したユーザ')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='childen', to='todo.Task', verbose_name='親タスク')),
                ('root', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rev_root', to='todo.Task', verbose_name='ルートタスク')),
                ('tags', models.ManyToManyField(blank=True, help_text='\n            <p>タスクにタグを付けて管理できます. 子孫にも継承されます. </p>\n            <p>非共有タグをタスクに登録した場合, 該当タスクにアクセス可能なユーザ全員に共有されます.</p>\n        ', to='todo.Tag', verbose_name='タグ')),
            ],
            options={
                'verbose_name': 'タスク',
                'verbose_name_plural': 'タスク',
            },
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('name', models.CharField(max_length=64, verbose_name='グループ名')),
                ('auto_created', models.BooleanField(default=False, verbose_name='システム管理オブジェクト')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='ユーザ')),
            ],
            options={
                'verbose_name': 'ユーザグループ',
                'verbose_name_plural': 'ユーザグループ',
            },
        ),
        migrations.AddField(
            model_name='task',
            name='users',
            field=models.ManyToManyField(blank=True, help_text='ユーザとグループを組み合わせて複数指定できます. ルートタスク以外では省略できます.', to='todo.UserGroup', verbose_name='対象ユーザ(グループ)'),
        ),
    ]
