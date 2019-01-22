from django.contrib import admin

# Register your models here.
from modem_api.models import Modem, Operator, Service, Station, Answer

admin.site.register(Modem)
admin.site.register(Operator)
admin.site.register(Service)
admin.site.register(Answer)