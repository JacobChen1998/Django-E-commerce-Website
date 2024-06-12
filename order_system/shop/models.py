from django.db import models
from PIL import Image
from cfg import product_img_size

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > product_img_size[1] or img.width > product_img_size[0]:
            output_size = (product_img_size[0], product_img_size[1])
            img.thumbnail(output_size)
            img.save(self.image.path)


class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"