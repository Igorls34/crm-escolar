from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_…'),  # deixe exatamente o nome da última migração antes da 0003
    ]

    operations = [
        migrations.RemoveField(
            model_name='lead',
            name='curso_interesse',
        ),
        migrations.AddField(
            model_name='lead',
            name='cursos_interesse',
            field=models.ManyToManyField(
                to='core.Curso',
                blank=True,
            ),
        ),
    ]
