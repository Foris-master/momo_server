from django.contrib import admin

# Register your models here.
from momo_api.models import Proof, Transaction, MobileWallet


class MobileWalletAdmin(admin.ModelAdmin):
    model = MobileWallet
    filter_horizontal = ('stations',)


admin.site.register(Proof)
admin.site.register(Transaction)
admin.site.register(MobileWallet, MobileWalletAdmin)
