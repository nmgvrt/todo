from django.contrib.auth import forms as auth_forms

from app.forms import *

from .models import MyUser

__all__ = ['CreateUserForm', 'EditUserForm']


class CreateUserForm(auth_forms.UserCreationForm):
    required_css_class = 'required'

    class Meta(auth_forms.UserCreationForm.Meta):
        model = MyUser
        fields = [
            'username', 'password1', 'password2',
            'last_name', 'first_name', 'is_superuser']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in ['last_name', 'first_name']:
            self.fields[key].required = True


class EditUserForm(CustomModelForm):
    required = ['last_name', 'first_name']

    class Meta:
        model = MyUser
        fields = ['last_name', 'first_name', 'is_superuser']
