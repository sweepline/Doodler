from django.contrib import admin

from doodler.models import Doodle


@admin.register(Doodle)
class DoodleAdmin(admin.ModelAdmin):
    list_display = ("name",)
