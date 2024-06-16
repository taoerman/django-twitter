# Generated by Django 3.2.25 on 2024-06-13 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0005_tweetphoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='comments_count',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='tweet',
            name='likes_count',
            field=models.IntegerField(default=0, null=True),
        ),
    ]