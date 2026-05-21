#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell << END
from users.models import User
import os
phone = os.getenv("ADMIN_PHONE", "+998901234567")
password = os.getenv("ADMIN_PASSWORD", "admin123")
if not User.objects.filter(phone=phone).exists():
    User.objects.create_superuser(phone=phone, password=password)
    print(f"Superuser created with phone: {phone}")
else:
    print(f"Superuser with phone {phone} already exists")
END
