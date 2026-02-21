from decimal import Decimal
from django.conf import settings
from apps.store.models import ProductVariant


class Cart:
    """سبد خرید مبتنی بر Session"""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, variant, quantity=1, override_quantity=False):
        variant_id = str(variant.id)
        if variant_id not in self.cart:
            self.cart[variant_id] = {
                'quantity': 0,
                'price': str(variant.product.final_price),
                'product_id': str(variant.product.id),
            }
        if override_quantity:
            self.cart[variant_id]['quantity'] = quantity
        else:
            self.cart[variant_id]['quantity'] += quantity
        self.save()

    def remove(self, variant):
        variant_id = str(variant.id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        del self.session['cart']
        self.save()

    def __iter__(self):
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(id__in=variant_ids).select_related(
            'product', 'size', 'color'
        )
        cart = self.cart.copy()
        for variant in variants:
            cart[str(variant.id)]['variant'] = variant
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    @property
    def total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    @property
    def shipping_cost(self):
        threshold = getattr(settings, 'FREE_SHIPPING_THRESHOLD', 500000)
        if self.total_price >= threshold:
            return Decimal(0)
        return Decimal(getattr(settings, 'DEFAULT_SHIPPING_COST', 35000))

    @property
    def grand_total(self):
        return self.total_price + self.shipping_cost
