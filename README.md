# ShopEase - E-Commerce Website

## Setup Instructions

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run migrations:
```
python manage.py makemigrations
python manage.py migrate
```

3. Load sample data:
```
python manage.py shell < setup_data.py
```

4. Run server:
```
python manage.py runserver
```

5. Open: http://127.0.0.1:8000

## Login Credentials
- **Admin:** admin / admin123
- **User 1:** user1 / pass123

## Coupon Codes (demo)
- **SAVE10** - 10% off on orders ₹500+
- **FIRST20** - 20% off on orders ₹1000+
- **FLAT50** - 5% off on orders ₹200+

## Features
- Product listing with search, filter, sort
- Shopping cart (add, update, remove)
- Secure checkout with multiple payment options
- Order management & tracking
- Product reviews & ratings
- Wishlist
- Coupon code system
- Beautiful responsive UI
