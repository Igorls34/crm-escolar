from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import migrations

def create_super_user(apps, schema_editor):
    User = get_user_model()
    username = settings.DJANGO_SUPERUSER_USERNAME
    email    = settings.DJANGO_SUPERUSER_EMAIL
    password = settings.DJANGO_SUPERUSER_PASSWORD

    if username and password and not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username=username,
            email=email or '',
            password=password,
        )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_curso_interesse_add_m2m'),
    ]

    operations = [
        migrations.RunPython(create_super_user),
    ]
