# Generated by Django 4.1 on 2024-02-18 03:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_remove_customuser_investor_role_and_more'),
    ]

    operations = [

        migrations.CreateModel(
            name='Companies',
            fields=[
                ('company_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(blank=True, max_length=255)),
                ('is_registered', models.BooleanField(default=False)),
                ('common_info', models.TextField(blank=True)),
                ('contact_phone', models.CharField(blank=True, max_length=255)),
                ('contact_email', models.CharField(blank=True, max_length=255)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('edrpou', models.IntegerField(blank=True, null=True)),
                ('address', models.TextField(blank=True, max_length=255)),
                ('product_info', models.TextField(blank=True)),
                ('startup_idea', models.TextField(blank=True)),
                ('tags', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='id',
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_id',
            field=models.BigAutoField(auto_created=True, default=0, primary_key=True, serialize=False, unique=True),
        ),
        migrations.CreateModel(
            name='CompaniesAndUsersRelations',
            fields=[
                ('relation_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('position', models.IntegerField()),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.companies')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.customuser')),
            ],
        ),
    ]
