from django.contrib import admin

# Register your models here.
from modem_api.models import Modem, Operator, Service, Station, Answer, ServiceStation, OperatorService

admin.site.register(Modem)
admin.site.register(Operator)
admin.site.register(Service)
admin.site.register(Answer)
admin.site.register(Station)
admin.site.register(OperatorService)
admin.site.register(ServiceStation)
