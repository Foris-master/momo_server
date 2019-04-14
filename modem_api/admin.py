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


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Modem)
admin.site.register(Operator)
admin.site.register(Service)
admin.site.register(Answer)
admin.site.register(Station)
admin.site.register(OperatorService)
admin.site.register(ServiceStation)
