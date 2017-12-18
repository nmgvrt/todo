__all__ = [
    'CustomFormFieldMixin'
]


class CustomFormFieldMixin(object):
    def set_additional_data(self, data):
        for key, val in data.items():
            if hasattr(self, key):
                raise Exception('{} クラスにはすでに属性 : {} が存在します'.format(
                    self.__class__.__name__, key))
            setattr(self, key, val)

    def set_new_queryset(self, *args, **kwargs):
        pass
