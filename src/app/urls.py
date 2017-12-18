"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import reverse_lazy
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView, RedirectView

from . import views

urlpatterns = [
    url(r'^$', TemplateView.as_view(
        template_name='base/index.html'), name='index'),
    url(r'^auth/', include('cauth.urls')),
    url(r'^todo/', include('todo.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login,
        {'template_name': 'auth/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^logout_then_login/$',
        auth_views.logout_then_login, name='logout_then_login'),
    url(r'^change_password_(?P<pk>\d+)/$',
        auth_views.PasswordChangeView.as_view(
            template_name='auth/change_password.html',
            success_url=reverse_lazy('index')), name='change_password'),
    url(r'^error/$', views.error, name='error'),
]
