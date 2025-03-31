# Generated by Django 5.1.6 on 2025-03-26 17:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speech_processing', '0003_category_expectedspeech_order_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('native_name', models.CharField(blank=True, max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('flag_code', models.CharField(blank=True, max_length=10)),
            ],
            options={
                'verbose_name': 'Language',
                'verbose_name_plural': 'Languages',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='expectedspeech',
            name='difficulty_level',
            field=models.IntegerField(choices=[(1, 'Beginner'), (2, 'Intermediate'), (3, 'Advanced')], default=1),
        ),
        migrations.AddField(
            model_name='expectedspeech',
            name='phonetic_transcription',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='speechrecord',
            name='accuracy_score',
            field=models.FloatField(blank=True, help_text='Percentage of correct pronunciation', null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='speech_processing.language'),
        ),
        migrations.AddField(
            model_name='expectedspeech',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='speech_items', to='speech_processing.language'),
        ),
        migrations.AddField(
            model_name='speechrecord',
            name='language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='speech_records', to='speech_processing.language'),
        ),
        migrations.CreateModel(
            name='PronunciationResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_type', models.CharField(choices=[('audio', 'Audio'), ('video', 'Video'), ('text', 'Text Guide')], max_length=50)),
                ('url', models.URLField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('expected_speech', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='speech_processing.expectedspeech')),
            ],
        ),
    ]
