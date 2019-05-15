from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from modem_api.models import Profile, Modem, Operator, Service, Station, Answer, ServiceStation, OperatorService


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'admins'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


class ModemAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag', 'is_active', 'description', 'updated_at')


class OperatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag', 'country', 'description', 'updated_at')


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag', 'description', 'updated_at')


class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_merchant', 'state', 'phone_number', 'modem', 'operator', 'imei', 'updated_at')


class OperatorServiceAdmin(admin.ModelAdmin):
    list_display = ('ussd', 'operator', 'service', 'answer', 'updated_at')


class ServiceStationAdmin(admin.ModelAdmin):
    list_display = ('balance', 'pin', 'service', 'station', 'updated_at')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('parent', 'answer', 'is_int', 'order', 'description', 'updated_at')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Answer, AnswerAdmin)
admin.site.register(Modem, ModemAdmin)
admin.site.register(Operator, OperatorAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(OperatorService, OperatorServiceAdmin)
admin.site.register(ServiceStation, ServiceStationAdmin)
