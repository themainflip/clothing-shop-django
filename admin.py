from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address, LoyaltyTransaction, WalletTransaction, GiftCard


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone', 'loyalty_points', 'wallet_balance', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات تکمیلی', {'fields': ('phone', 'gender', 'birth_date', 'avatar', 'national_code')}),
        ('امتیاز و کیف پول', {'fields': ('loyalty_points', 'wallet_balance')}),
        ('تنظیمات', {'fields': ('newsletter', 'sms_notifications', 'email_notifications', 'two_factor_enabled')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'city', 'province', 'is_default']


@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ['code', 'initial_amount', 'remaining_amount', 'is_active', 'expiry_date']
    list_editable = ['is_active']
