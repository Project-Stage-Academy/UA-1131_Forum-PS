# Generated by Django 4.1.13 on 2024-02-29 21:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_customuser_phone_number_alter_customuser_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('company_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(blank=True, max_length=255)),
                ('is_startup', models.BooleanField(default=False)),
                ('common_info', models.TextField(blank=True)),
                ('contact_phone', models.CharField(blank=True, max_length=255)),
                ('contact_email', models.CharField(blank=True, max_length=255)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('edrpou', models.IntegerField(null=True)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('product_info', models.TextField(blank=True)),
                ('startup_idea', models.TextField(blank=True)),
                ('tags', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='id',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='last_login',
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_id',
            field=models.BigAutoField(primary_key=True, serialize=False, unique=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='CompanyAndUserRelation',
            fields=[
                ('relation_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('position', models.CharField(choices=[('F', 'Founder'), ('R', 'Representative')], default='R', max_length=30)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.company')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]