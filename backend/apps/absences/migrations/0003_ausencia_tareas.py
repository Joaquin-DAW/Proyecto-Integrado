from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('absences', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ausencia',
            name='tareas',
            field=models.TextField(blank=True, default=''),
        ),
    ]
