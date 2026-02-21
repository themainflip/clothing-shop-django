from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    GENDER_CHOICES = [
        ('male', 'آقا'),
        ('female', 'خانم'),
        ('other', 'ترجیح می‌دهم نگویم'),
    ]
    phone = models.CharField('شماره موبایل', max_length=11, blank=True)
    gender = models.CharField('جنسیت', max_length=10, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField('تاریخ تولد', null=True, blank=True)
    avatar = models.ImageField('تصویر پروفایل', upload_to='avatars/', blank=True)
    national_code = models.CharField('کد ملی', max_length=10, blank=True)
    
    # Loyalty
    loyalty_points = models.PositiveIntegerField('امتیاز وفاداری', default=0)
    wallet_balance = models.DecimalField('موجودی کیف پول', max_digits=12, decimal_places=0, default=0)
    
    # Preferences
    newsletter = models.BooleanField('عضویت خبرنامه', default=True)
    sms_notifications = models.BooleanField('اعلان پیامکی', default=True)
    email_notifications = models.BooleanField('اعلان ایمیلی', default=True)
    
    # 2FA
    two_factor_enabled = models.BooleanField('احراز هویت دومرحله‌ای', default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def total_orders(self):
        return self.orders.count()


class Address(models.Model):
    PROVINCE_CHOICES = [
        ('tehran', 'تهران'), ('isfahan', 'اصفهان'), ('mashhad', 'مشهد'),
        ('shiraz', 'شیراز'), ('tabriz', 'تبریز'), ('ahvaz', 'اهواز'),
        ('qom', 'قم'), ('kermanshah', 'کرمانشاه'), ('other', 'سایر'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField('عنوان آدرس', max_length=100)  # خانه، محل کار
    receiver_name = models.CharField('نام تحویل‌گیرنده', max_length=200)
    receiver_phone = models.CharField('شماره تحویل‌گیرنده', max_length=11)
    province = models.CharField('استان', max_length=100, choices=PROVINCE_CHOICES)
    city = models.CharField('شهر', max_length=100)
    address = models.TextField('آدرس کامل')
    postal_code = models.CharField('کد پستی', max_length=10)
    is_default = models.BooleanField('پیش‌فرض', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس‌ها'

    def __str__(self):
        return f"{self.title} - {self.city}"


class LoyaltyTransaction(models.Model):
    TYPE_CHOICES = [
        ('earn', 'کسب امتیاز'),
        ('spend', 'استفاده از امتیاز'),
        ('expire', 'انقضا'),
        ('bonus', 'امتیاز هدیه'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loyalty_transactions')
    transaction_type = models.CharField('نوع', max_length=10, choices=TYPE_CHOICES)
    points = models.IntegerField('امتیاز')
    description = models.CharField('توضیح', max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تراکنش امتیاز'
        verbose_name_plural = 'تراکنش‌های امتیاز'

    def __str__(self):
        return f"{self.user} - {self.points} امتیاز"


class WalletTransaction(models.Model):
    TYPE_CHOICES = [
        ('deposit', 'شارژ'),
        ('withdraw', 'برداشت'),
        ('refund', 'بازگشت وجه'),
        ('purchase', 'خرید'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transactions')
    transaction_type = models.CharField('نوع', max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField('مبلغ', max_digits=12, decimal_places=0)
    balance_after = models.DecimalField('موجودی بعد', max_digits=12, decimal_places=0)
    description = models.CharField('توضیح', max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تراکنش کیف پول'
        verbose_name_plural = 'تراکنش‌های کیف پول'


class GiftCard(models.Model):
    code = models.CharField('کد کارت', max_length=20, unique=True)
    initial_amount = models.DecimalField('مبلغ اولیه', max_digits=12, decimal_places=0)
    remaining_amount = models.DecimalField('موجودی باقی‌مانده', max_digits=12, decimal_places=0)
    issued_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='gift_cards_received')
    purchased_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='gift_cards_purchased')
    expiry_date = models.DateField('تاریخ انقضا')
    is_active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'کارت هدیه'
        verbose_name_plural = 'کارت‌های هدیه'

    def __str__(self):
        return self.code
