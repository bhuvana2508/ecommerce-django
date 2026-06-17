#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell << 'EOF'
from django.contrib.auth.models import User
if User.objects.filter(username='admin').exists():
    u = User.objects.get(username='admin')
    u.set_password('admin123')
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print("Password reset to admin123")
else:
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created")
EOF