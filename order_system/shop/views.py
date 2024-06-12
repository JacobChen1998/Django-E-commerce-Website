from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
import cfg
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

from .models import Product, Category, Order, OrderItem
# from .models import Product, Category
# from .models import Category

from .forms import OrderForm
from django.http import JsonResponse

import cfg
from cfg import product_img_size,providerEmail,providerEmailPWD
from cfg import mail_adress_receiver,mail_adress_sender,sendMail,sendLine
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from order_system.settings import BASE_DIR

import os
from django.conf import settings

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Product
from .forms import OrderForm

import queue, threading
import time

CART_SESSION_ID = 'cart'

from utils import load_products_from_file, save_products_to_file

def product_list(request, category_id=None):
    grid_size = (4, 5)  # 默认的 grid_size 可以从 cfg.py 中读取
    categories = load_products_from_file()
    products = []
    if category_id:
        category_name = get_object_or_404(Category, id=category_id).name
        products = categories.get(category_name, [])
    else:
        for product_list in categories.values():
            products.extend(product_list)

    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    # 计算每个产品的列宽
    column_width = 12 // grid_size[1]

    context = {
        'categories': categories,
        'products': products,
        'product_img_size': cfg.product_img_size,
        'column_width': column_width,  # 传递计算的列宽
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.save()
            # 这里可以添加发送通知的逻辑
            send_notification_email(order)

            return redirect('product_list')
    else:
        form = OrderForm()
    context = {
        'product': product,
        'form': form,
        'product_img_size': cfg.product_img_size,  # 传递图片大小参数
    }
    return render(request, 'shop/product_detail.html', context)

def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
    request.session['cart'] = cart
    return redirect('cart_detail')

# 清空購物車視圖函數
def cart_clear(request):
    request.session['cart'] = {}
    return redirect('cart_detail')

def checkout(request):
    cart = request.session.get(CART_SESSION_ID, {})
    if request.method == 'POST':
        for item_id, item in cart.items():
            product = get_object_or_404(Product, id=item_id)
            send_notification_email(product, item['quantity'])

        request.session[CART_SESSION_ID] = {}
        return redirect('product_list')

    return render(request, 'shop/checkout.html')

def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {'quantity': quantity, 'price': str(product.price)}
    
    request.session['cart'] = cart
    return JsonResponse({'status': 'success'})

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    for product in products:
        product_id_str = str(product.id)
        cart_items.append({
            'product': product,
            'quantity': cart[product_id_str]['quantity'],
            'price': cart[product_id_str]['price'],
        })

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            order_items = []
            for item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price']  # Add the price here
                )
                order_items.append(order_item)
            send_notification_email(order, order_items)
            request.session['cart'] = {}  # Clear the cart
            return redirect('product_list')
    else:
        form = OrderForm()

    context = {
        'cart_items': cart_items,
        'form': form,
    }
    return render(request, 'shop/cart_detail.html', context)

def cart_update(request, product_id):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))
    product_id_str = str(product_id)
    if quantity > 0:
        cart[product_id_str]['quantity'] = quantity
    else:
        cart.pop(product_id_str, None)
    request.session['cart'] = cart
    return redirect('cart_detail')


def send_notification_email(order,order_items):
    subject = f'New Order {order.id} ({order.customer_name})'
    message = f'You have a new order from {order.customer_name}\n'
    message += f"  PHONE : {({order.phone})}\n"
    message += f"  Mail : ({order.email})\n"

    for item in order_items:
        message += f'{item.product.name}: {item.quantity} x ${item.product.price}\n'

    if sendMail:
        msg = MIMEMultipart()
        msg['From'] = mail_adress_sender
        msg['To'] = mail_adress_receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        # 4. 添加ZIP附件
        # attachment = open(zip_filename, "rb")
        # part = MIMEBase('application', 'zip')
        # part.set_payload((attachment).read())
        # encoders.encode_base64(part)
        # part.add_header('Content-Disposition', "attachment; filename= %s" % zip_filename)
        # msg.attach(part)
        print("Mail content : ")
        print(msg.as_string())
        smtp_server = "smtp.gmail.com"
        smtp_port = 587  # 一般为587或465
        smtp_username = providerEmail
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, providerEmailPWD)
            server.sendmail(mail_adress_sender, mail_adress_receiver, msg.as_string())
            server.quit()
            print('Send mail successful')
        except Exception as e:
            print("Error message: ", e)
    if sendLine:
        print(1233333333333333333333)

def load_products():
    products = []
    categories = {}
    with open(os.path.join(settings.BASE_DIR, 'products.txt'), 'r', encoding='utf-8') as f:
        category_name = None
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("'") and line.endswith("'"):
                category_name = line.strip("'")
                if category_name not in categories:
                    categories[category_name], _ = Category.objects.get_or_create(name=category_name)
            else:
                parts = line.split()
                if len(parts) < 4:
                    continue
                parts = parts[1:]
                name = parts[0]
                image_path = parts[1]
                image_path = os.path.join('products', os.path.basename(image_path))  # 更新路径
                price = float(parts[2])
                quantity = int(parts[3])
                product, created = Product.objects.get_or_create(
                    name=name,
                    image=image_path,
                    defaults={'price': price, 'quantity': quantity, 'category': categories[category_name]}
                )
                if created:
                    product.price = price
                    product.quantity = quantity
                    product.category = categories[category_name]
                    product.save()
                products.append(product)
    return products

def update_products():
    products = load_products()
    for product in products:
        product.save()


def updateProductQ(queue):

    update_products()
    print('update product ...................')
    time.sleep(1)



updateQ = queue.Queue()
tR = threading.Thread(target = updateProductQ, args = (updateQ,))
tR.setDaemon(True)
tR.start()
