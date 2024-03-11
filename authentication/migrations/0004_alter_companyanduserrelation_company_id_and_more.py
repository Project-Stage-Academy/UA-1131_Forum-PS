# Generated by Django 4.1.13 on 2024-03-07 09:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_company_remove_customuser_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyanduserrelation',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_relations', to='authentication.company'),
        ),
        migrations.AlterField(
            model_name='companyanduserrelation',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_relations', to=settings.AUTH_USER_MODEL),
        ),
    ]