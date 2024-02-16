# Generated by Django 5.0.2 on 2024-02-16 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0002_alter_message_chat'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='visible_for_recipient',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='message',
            name='visible_for_sender',
            field=models.BooleanField(default=True),
        ),
    ]
