from django.contrib import admin

# Register your models here.
from momo_api.models import Proof, Transaction, MobileWallet

admin.site.register(Proof)
admin.site.register(Transaction)
admin.site.register(MobileWallet)
