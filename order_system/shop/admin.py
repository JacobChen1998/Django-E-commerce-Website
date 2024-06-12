# from django.contrib import admin
# # from .models import Product, Order
# from .models import Product, Category

# admin.site.register(Product)
# # admin.site.register(Order)
# admin.site.register(Category)

from django.contrib import admin
from django import forms
from .models import Product, Category
from utils import load_products_from_file, save_products_to_file

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'image', 'price', 'quantity', 'description']

    def save(self, commit=True):
        instance = super().save(commit=False)
        categories = load_products_from_file()
        for cat_name, products in categories.items():
            if cat_name == instance.category.name:
                for product in products:
                    if product['name'] == instance.name:
                        product['quantity'] = instance.quantity
                        product['price'] = instance.price
                        break
        save_products_to_file(categories)
        if commit:
            instance.save()
        return instance

class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
