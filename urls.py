from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.store.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('orders/', include('apps.orders.urls')),
    path('cart/', include('apps.cart.urls')),
    path('vendors/', include('apps.vendors.urls')),
    path('blog/', include('apps.blog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'مدیریت فروشگاه مد'
admin.site.site_title = 'FashionStore Admin'
admin.site.index_title = 'پنل مدیریت'
