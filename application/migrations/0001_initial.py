# Generated by Django 4.2.1 on 2023-05-28 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SomeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Чтоб было')),
            ],
            options={
                'verbose_name': 'Модель',
                'verbose_name_plural': 'Модели',
                'ordering': ('-pk',),
            },
        ),
    ]
