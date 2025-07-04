from django.contrib.auth import get_user_model
from django.db import migrations

def create_super_user(apps, schema_editor):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='Igor',
            email='igorlaurindo49@gmail.com',
            password='admin@2025b'
        )

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_super_user),
    ]
