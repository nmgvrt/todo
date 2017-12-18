from django.urls import reverse_lazy
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView, RedirectView

from . import views
from .generic import *

urlpatterns = [
    url(r'^admin/users/$', UserListView.as_view(
        template_name='auth/myusers.html'), name='admin_users'),
    url(r'^admin/add_user/$', UserCreateView.as_view(
        template_name='auth/add_myuser.html'), name='admin_add_user'),
    url(r'^admin/edit_user_(?P<pk>\d+)/$', UserUpdateView.as_view(
        template_name='auth/edit_myuser.html'), name='admin_edit_user'),
    url(r'^admin/delete_user_(?P<pk>\d+)/$', UserDeleteView.as_view(
        template_name='auth/delete_myuser.html'), name='admin_delete_user'),
]
