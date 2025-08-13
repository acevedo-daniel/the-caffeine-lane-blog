from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0001_initial'),  # ← Cambia esto si tu migración inicial tiene otro nombre
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='excerpt',
            field=models.CharField(
                max_length=300,
                blank=True,
                verbose_name='Extracto',
                help_text='Breve descripción del post para mostrar en listados'
            ),
        ),
    ]