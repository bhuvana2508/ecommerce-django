"""python manage.py shell < setup_data.py"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
import django
django.setup()

from django.contrib.auth.models import User
from store.models import *

print("Creating users...")
admin = User.objects.create_superuser('admin', 'admin@shop.com', 'admin123', first_name='Admin')
user1 = User.objects.create_user('user1', 'user1@shop.com', 'pass123', first_name='Alice', last_name='Smith')
user2 = User.objects.create_user('user2', 'user2@shop.com', 'pass123', first_name='Bob', last_name='Jones')

print("Creating categories...")
electronics = Category.objects.create(name='Electronics', slug='electronics', description='Gadgets and electronics')
fashion = Category.objects.create(name='Fashion', slug='fashion', description='Clothing and accessories')
books = Category.objects.create(name='Books', slug='books', description='Books and literature')
home = Category.objects.create(name='Home & Kitchen', slug='home-kitchen', description='Home essentials')
sports = Category.objects.create(name='Sports', slug='sports', description='Sports and fitness')

print("Creating products...")
products_data = [
    ('Wireless Bluetooth Headphones', electronics, 1999, 3499, 'Premium wireless headphones with 40hr battery life, ANC, foldable design. Crystal clear sound with deep bass.', 50, True),
    ('Smartwatch Pro X', electronics, 8999, 12999, 'Feature-packed smartwatch with health monitoring, GPS, 5ATM water resistance, 7-day battery.', 30, True),
    ('USB-C Fast Charger 65W', electronics, 899, 1299, 'GaN 65W USB-C fast charger compatible with laptops, phones, tablets.', 100, False),
    ('Premium Casual Sneakers', fashion, 1499, 2499, 'Comfortable daily wear sneakers with memory foam insole. Available in multiple colors.', 80, True),
    ('Men\'s Slim Fit Jeans', fashion, 999, 1799, 'Stretch denim slim fit jeans. Modern cut, comfortable waistband.', 120, False),
    ('Women\'s Floral Dress', fashion, 799, 1299, 'Lightweight summer dress with beautiful floral print. Machine washable.', 60, True),
    ('The Psychology of Money', books, 399, 599, 'Timeless lessons on wealth, greed and happiness. Morgan Housel\'s bestselling personal finance book.', 200, True),
    ('Atomic Habits', books, 349, 499, 'An easy and proven way to build good habits and break bad ones by James Clear.', 300, True),
    ('Stainless Steel Water Bottle', home, 499, 799, '1 litre vacuum insulated bottle. Keeps drinks cold 24hrs, hot 12hrs.', 150, False),
    ('Air Fryer 4.5L', home, 4999, 7999, 'Digital air fryer with 8 preset programs. 360° hot air circulation.', 40, True),
    ('Yoga Mat Premium', sports, 799, 1299, 'Non-slip 6mm thick eco-friendly yoga mat with carrying strap.', 75, False),
    ('Resistance Band Set', sports, 599, 899, 'Set of 5 resistance bands with carrying bag. Perfect for home workouts.', 90, True),
]
for name, cat, price, orig, desc, stock, featured in products_data:
    Product.objects.create(name=name, category=cat, price=price, original_price=orig,
                           description=desc, stock=stock, is_featured=featured, is_active=True)

print("Creating reviews...")
from store.models import Review, Product
p1 = Product.objects.get(name__contains='Headphones')
p2 = Product.objects.get(name__contains='Atomic')
Review.objects.create(product=p1, user=user1, rating=5, comment='Excellent sound quality! The ANC is amazing.')
Review.objects.create(product=p1, user=user2, rating=4, comment='Great headphones, very comfortable.')
Review.objects.create(product=p2, user=user1, rating=5, comment='Life-changing book. Highly recommended!')

print("Creating coupons...")
from datetime import date, timedelta
Coupon.objects.create(code='SAVE10', discount_percent=10, minimum_amount=500, is_active=True, expiry_date=date.today()+timedelta(days=30))
Coupon.objects.create(code='FIRST20', discount_percent=20, minimum_amount=1000, is_active=True, expiry_date=date.today()+timedelta(days=30))
Coupon.objects.create(code='FLAT50', discount_percent=5, minimum_amount=200, is_active=True, expiry_date=date.today()+timedelta(days=30))

print("\n✅ E-Commerce data created!")
print("Login: admin/admin123, user1/pass123")
