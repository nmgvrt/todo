from django import forms

from .form_fields import *

__all__ = [
    'CustomModelForm'
]


class CustomModelForm(forms.ModelForm):
    additional_keys = ['user']

    required_css_class = 'required'
    required = []

    def __init__(self, *args, **kwargs):
        additional_data = {}

        for key in self.additional_keys:
            if key in kwargs:
                if hasattr(self, key):
                    raise Exception('{} クラスにはすでに属性 : {} が存在します'.format(
                        self.__class__.__name__, key))
                setattr(self, key, kwargs[key])
                additional_data[key] = kwargs[key]
                del kwargs[key]

        super(CustomModelForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields[field_name]
            if issubclass(field.__class__, CustomFormFieldMixin):
                field.set_additional_data(additional_data)
                field.set_new_queryset()

        for field_name in self.required:
            if field_name in self.fields:
                self.fields[field_name].required = True
