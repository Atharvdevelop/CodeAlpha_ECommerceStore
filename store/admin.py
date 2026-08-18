from django.contrib import admin
from .models import Category, Product, ProductVariant, Wishlist, Cart, CartItem, Order, OrderItem, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'product_count')
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('color_name', 'color_code', 'size', 'stock', 'price', 'variant_image')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    list_editable = ('price', 'stock', 'is_active')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')


class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ['product', 'variant']
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'get_total_items', 'get_total_price', 'created_at')
    inlines = [CartItemInline]
    search_fields = ('user__username', 'session_key')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product', 'variant']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'country')
    list_editable = ('status',)
    search_fields = ('full_name', 'email', 'address', 'city', 'id')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'total_price')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')



