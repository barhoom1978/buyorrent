# Generated by Django 3.0.6 on 2021-04-15 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buyorrent', '0011_auto_20210402_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenario',
            name='growth_ftse',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='growth_house',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='inflation',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='interest_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
