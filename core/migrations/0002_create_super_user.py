from django.db import migrations

def create_super_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    username = "admin"                  # ou o que você preferir
    email = "admin@exemplo.com"
    password = "SenhaSegura123"
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_super_user),
    ]
