from django.conf.urls import url
from django.views.generic import TemplateView

from app.generic import *

from . import views
from .generic import *

urlpatterns = [
    url(r'^$', TemplateView.as_view(
        template_name='todo/index.html'), name='todo_index'),
    url(r'^mypage/$', views.mypage, name='todo_mypage'),
    url(r'^calendar/$', views.earliest_month_calendar_view,
        name='earliest_month_calendar'),
    url(r'^calendar/(?P<year>2[01]\d{2})/(?P<month>\d{1,2})/$',
        views.calendar_view, name='calendar'),

    url(r'^public_tasks/$', PublicTaskListView.as_view(
        template_name='todo/public_tasks.html',
    ), name='public_tasks'),
    url(r'^finished_public_tasks/$', FinishedPublicTaskListView.as_view(
        template_name='todo/finished_public_tasks.html',
    ), name='finished_public_tasks'),
    url(r'^my_tasks/$', MyTaskListView.as_view(
        template_name='todo/my_tasks.html',
    ), name='my_tasks'),
    url(r'^finished_my_tasks/$', FinishedMyTaskListView.as_view(
        template_name='todo/finished_my_tasks.html',
    ), name='finished_my_tasks'),

    url(r'^public_tasks/tag_(?P<tag_pk>\d+)/$', PublicTaskListView.as_view(
        template_name='todo/public_tasks_tag.html',
    ), name='public_tasks_tag'),
    url(r'^finished_public_tasks/tag_(?P<tag_pk>\d+)/$',
        FinishedPublicTaskListView.as_view(
            template_name='todo/finished_public_tasks_tag.html',
        ), name='finished_public_tasks_tag'),
    url(r'^my_tasks/tag_(?P<tag_pk>\d+)/$', MyTaskListView.as_view(
        template_name='todo/my_tasks_tag.html',
    ), name='my_tasks_tag'),
    url(r'^finished_my_tasks/tag_(?P<tag_pk>\d+)/$',
        FinishedMyTaskListView.as_view(
            template_name='todo/finished_my_tasks_tag.html',
        ), name='finished_my_tasks_tag'),

    url(r'^public_tasks/usergroup_(?P<group_pk>\d+)/$', PublicTaskListView.as_view(
        template_name='todo/public_tasks_group.html',
    ), name='public_tasks_group'),
    url(r'^finished_public_tasks/usergroup_(?P<group_pk>\d+)/$',
        FinishedPublicTaskListView.as_view(
            template_name='todo/finished_public_tasks_group.html',
        ), name='finished_public_tasks_group'),
    url(r'^my_tasks/usergroup_(?P<group_pk>\d+)/$', MyTaskListView.as_view(
        template_name='todo/my_tasks_group.html',
    ), name='my_tasks_group'),
    url(r'^finished_my_tasks/usergroup_(?P<group_pk>\d+)/$',
        FinishedMyTaskListView.as_view(
            template_name='todo/finished_my_tasks_group.html',
        ), name='finished_my_tasks_group'),

    url(r'^add_task/$', views.add_task, name='add_task'),
    url(r'^add_child_task_(?P<pk>\d+)/$', views.add_child_task,
        name='add_child_task'),
    url(r'^task_detail_(?P<pk>\d+)/$', TaskDetailView.as_view(
        template_name='todo/task_detail.html'), name='task_detail'),
    url(r'^edit_task_(?P<pk>\d+)/$', views.edit_task, name='edit_task'),
    url(r'^delete_task_(?P<pk>\d+)/$', views.delete_task, name='delete_task'),
    url(r'^finish_task_(?P<pk>\d+)/$', views.finish_task, name='finish_task'),
    url(r'^change_my_state_(?P<pk>\d+)/$', views.change_my_state,
        name='change_my_state'),

    url(r'^my_tags/$', MyTagListView.as_view(
        template_name='todo/my_tags.html'
    ), name='my_tags'),
    url(r'^add_my_tag/$', MyTagCreateView.as_view(
        template_name='todo/add_tag.html'), name='add_my_tag'),
    url(r'^edit_tag_(?P<pk>\d+)/$', TagUpdateView.as_view(
        template_name='todo/edit_tag.html'), name='edit_tag'),
    url(r'^delete_tag_(?P<pk>\d+)/$', TagDeleteView.as_view(
        template_name='todo/delete_tag.html'), name='delete_tag'),

    url(r'^admin/tags/$', PublicTagListView.as_view(
        template_name='todo/tags.html'), name='admin_tags'),
    url(r'^admin/add_tag/$', AdminTagCreateView.as_view(
        template_name='todo/add_tag.html'), name='admin_add_tag'),
    url(r'^admin/edit_tag_(?P<pk>\d+)/$', TagUpdateView.as_view(
        template_name='todo/edit_tag.html'), name='admin_edit_tag'),

    url(r'^admin/usergroups/$', UserGroupListView.as_view(
        template_name='todo/usergroups.html'), name='admin_usergroups'),
    url(r'^admin/add_usergroup/$', UserGroupCreateView.as_view(
        template_name='todo/add_usergroup.html'), name='admin_add_usergroup'),
    url(r'^admin/edit_usergroup_(?P<pk>\d+)/$', UserGroupUpdateView.as_view(
        template_name='todo/edit_usergroup.html'),
        name='admin_edit_usergroup'),
    url(r'^admin/delete_usergroup_(?P<pk>\d+)/$', UserGroupDeleteView.as_view(
        template_name='todo/delete_usergroup.html'),
        name='admin_delete_usergroup'),

    url(r'^json/usergroup/user/$', views.json_usergroup_user,
        name='json_usergroup_user'),
    url(r'^json/usergroup/user/task_(?P<pk>\d+)/$',
        views.json_usergroup_user_child,
        name='json_usergroup_user_child'),
    url(r'^json/usergroup/user/task_(?P<pk>\d+)/edit/$',
        views.json_usergroup_user_child_edit,
        name='json_usergroup_user_child_edit'),

    url(r'^json/usergroup/group/$', views.json_usergroup_group,
        name='json_usergroup_group'),
    url(r'^json/usergroup/group/task_(?P<pk>\d+)/$',
        views.json_usergroup_group_child,
        name='json_usergroup_group_child'),
    url(r'^json/usergroup/group/task_(?P<pk>\d+)/edit/$',
        views.json_usergroup_group_child_edit,
        name='json_usergroup_group_child_edit'),

    url(r'^json/tag/public/$', views.json_tag_public,
        name='json_tag_public'),
    url(r'^json/tag/private/$', views.json_tag_private,
        name='json_tag_private'),
]
