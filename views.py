from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from .models import Address, LoyaltyTransaction, WalletTransaction

User = get_user_model()


def register(request):
    if request.user.is_authenticated:
        return redirect('store:home')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            messages.error(request, 'رمز عبورها مطابقت ندارند.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'این نام کاربری قبلاً ثبت شده است.')
            return render(request, 'accounts/register.html')
        
        user = User.objects.create_user(
            username=username, email=email, password=password, phone=phone
        )
        login(request, user)
        messages.success(request, f'خوش آمدید {user.username}! ثبت‌نام موفق.')
        return redirect('store:home')
    return render(request, 'accounts/register.html')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('store:home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'store:home')
            return redirect(next_url)
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    return redirect('store:home')


@login_required
def profile(request):
    from apps.orders.models import Order
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    context = {
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.gender = request.POST.get('gender', '')
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        user.save()
        messages.success(request, 'اطلاعات شما با موفقیت ویرایش شد.')
        return redirect('accounts:profile')
    return render(request, 'accounts/edit_profile.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        new_password2 = request.POST['new_password2']
        
        if not request.user.check_password(old_password):
            messages.error(request, 'رمز عبور فعلی اشتباه است.')
        elif new_password != new_password2:
            messages.error(request, 'رمز عبورهای جدید مطابقت ندارند.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'رمز عبور تغییر یافت.')
            return redirect('accounts:login')
    return render(request, 'accounts/change_password.html')


@login_required
def addresses(request):
    user_addresses = request.user.addresses.all()
    return render(request, 'accounts/addresses.html', {'addresses': user_addresses})


@login_required
def add_address(request):
    if request.method == 'POST':
        Address.objects.create(
            user=request.user,
            title=request.POST['title'],
            receiver_name=request.POST['receiver_name'],
            receiver_phone=request.POST['receiver_phone'],
            province=request.POST['province'],
            city=request.POST['city'],
            address=request.POST['address'],
            postal_code=request.POST['postal_code'],
            is_default=request.POST.get('is_default', False),
        )
        messages.success(request, 'آدرس جدید اضافه شد.')
        return redirect('accounts:addresses')
    return render(request, 'accounts/add_address.html', {'province_choices': Address.PROVINCE_CHOICES})


@login_required
def wallet(request):
    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-created_at')[:20]
    return render(request, 'accounts/wallet.html', {'transactions': transactions})


@login_required
def loyalty_points(request):
    transactions = LoyaltyTransaction.objects.filter(user=request.user).order_by('-created_at')[:20]
    return render(request, 'accounts/loyalty.html', {'transactions': transactions})


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'حساب کاربری شما حذف شد.')
        return redirect('store:home')
    return render(request, 'accounts/delete_account.html')
