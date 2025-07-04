from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import migrations

def create_super_user(apps, schema_editor):
    User = get_user_model()
    username = settings.DJANGO_SUPERUSER_USERNAME
    email = settings.DJANGO_SUPERUSER_EMAIL
    password = settings.DJANGO_SUPERUSER_PASSWORD
    if username and password and not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_create_super_user'),  # substitua pelo nome da sua última migração
    ]
    operations = [
        migrations.RunPython(create_super_user),
    ]
