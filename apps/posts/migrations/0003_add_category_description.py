# posts/migrations/0003_add_category_description.py
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0002_add_excerpt'),  # ← CAMBIA esto por el nombre de tu última migración
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(
                blank=True,
                verbose_name='Descripción'
            ),
        ),
    ]