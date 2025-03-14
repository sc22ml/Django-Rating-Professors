# Generated by Django 5.1.6 on 2025-03-05 20:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rating_professors', '0004_alter_moduleinstance_year_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='comment',
        ),
        migrations.AlterField(
            model_name='rating',
            name='module_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rating_professors.moduleinstance'),
        ),
        migrations.AlterField(
            model_name='rating',
            name='professor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rating_professors.professor'),
        ),
        migrations.AlterField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
