from django.db import migrations

def create_super_user(apps, schema_editor):
    # Importa o modelo real de User
    User = apps.get_model('auth', 'User')
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='Igor',
            email='igorlaurindo49@gmail.com',
            password='123'
        )

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_super_user),
    ]
