# check_users.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

users = User.objects.all()
if users:
    for user in users:
        print(f"Username: {user.username}, Email: {user.email}, Is superuser: {user.is_superuser}")
else:
    print("Нет пользователей в базе данных!")