# Generated by Django 3.2.5 on 2021-09-06 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pybo_site', '0002_alter_question_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='content',
            field=models.TextField(verbose_name='답변내용'),
        ),
    ]