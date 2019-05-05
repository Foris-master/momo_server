from django.contrib import admin

# Register your models here.
from momo_api.models import Proof, Transaction, MobileWallet


class MobileWalletAdmin(admin.ModelAdmin):
    model = MobileWallet
    filter_horizontal = ('stations',)


class ProofInline(admin.TabularInline):
    model = Proof


class TransactionAdmin(admin.ModelAdmin):
    list_filter = ('status', 'created_at')
    list_display = ('amount', 'recipient', 'status', 'display_proof', 'created_at', 'updated_at')
    inlines = [ProofInline]


admin.site.register(Proof)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(MobileWallet, MobileWalletAdmin)
