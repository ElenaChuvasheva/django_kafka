from django.contrib import admin

from application.models import SomeModel


@admin.register(SomeModel)
class SomeModelAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name',)
