from django.http import Http404, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    DetailView, ListView, CreateView, UpdateView, DeleteView)

from app.decorators import *

__all__ = [
    'ListViewAuth', 'ListViewSuper', 'CreateViewSuper',
    'ActiveObjectDetailView', 'ActiveObjectDetailViewAuth',
    'CustomCreateView', 'CreateViewAuth', 'CreateViewSuper',
    'ActiveObjectUpdateView', 'ActiveObjectUpdateViewAuth',
    'ActiveObjectUpdateViewSuper',
    'DeactivateView', 'DeactivateViewAuth', 'DeactivateViewSuper'
]


@method_decorator(login_required, name='dispatch')
class ListViewAuth(ListView):
    pass


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class ListViewSuper(ListViewAuth):
    pass


class CheckIsActiveMixin(object):
    def render_to_response(self, *args, **kwargs):
        """
        オブジェクトが非アクティブなら 404
        """
        if self.object.is_active:
            return super().render_to_response(*args, **kwargs)
        else:
            raise Http404


class ActiveObjectDetailView(CheckIsActiveMixin, DetailView):
    """
    非アクティブなオブジェクトのとき 404 を投げる詳細ビュー

    アクセス制御 :
      指定された pk でオブジェクトが存在しないとき 404
      オブジェクトがアクティブでないとき 404
    """
    pass


@method_decorator(login_required, name='dispatch')
class ActiveObjectDetailViewAuth(ActiveObjectDetailView):
    pass


class CustomCreateView(CreateView):
    """
    オブジェクトの生成時に初期値をシステム側で管理する生成ビュー
    (フォームとしては扱わない値の初期値を制御)
    """
    def set_initial(self, instance):
        """
        初期値を変更する
        派生クラス用ホック
        """
        pass

    def form_valid(self, form):
        # フォームの検証成功時に初期値を設定する
        self.set_initial(form.instance)

        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class CreateViewAuth(CustomCreateView):
    pass


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class CreateViewSuper(CreateViewAuth):
    pass


class ActiveObjectUpdateView(CheckIsActiveMixin, UpdateView):
    """
    非アクティブなオブジェクトのとき 404 を投げる詳細ビュー

    アクセス制御 :
      指定された pk でオブジェクトが存在しないとき 404
      オブジェクトがアクティブでないとき 404
    """
    pass


@method_decorator(login_required, name='dispatch')
class ActiveObjectUpdateViewAuth(ActiveObjectUpdateView):
    pass


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class ActiveObjectUpdateViewSuper(ActiveObjectUpdateViewAuth):
    pass


class DeactivateView(CheckIsActiveMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.deactivate()

        return HttpResponseRedirect(success_url)


@method_decorator(login_required, name='dispatch')
class DeactivateViewAuth(DeactivateView):
    pass


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class DeactivateViewSuper(DeactivateViewAuth):
    pass
