# posts/migrations/0004_add_comment_is_edited.py
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0003_add_category_description'),  # ← CAMBIA esto por tu última migración
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_edited',
            field=models.BooleanField(
                default=False,
                verbose_name='Editado'
            ),
        ),
    ]