from randopony.pony.models import Member, Brevet, Result
from django.contrib import admin


class ResultInLine(admin.StackedInline):
    model = Result
    extra = 5


class BrevetAdmin(admin.ModelAdmin):
    inlines = [ResultInLine]

admin.site.register(Member)
admin.site.register(Brevet, BrevetAdmin)
admin.site.register(Result)
