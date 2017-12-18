from django.contrib import admin

from .models import Color, Tag, UserGroup, Task

admin.site.register(Color)
admin.site.register(Tag)
admin.site.register(UserGroup)
admin.site.register(Task)
