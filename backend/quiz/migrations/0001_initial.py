# Generated by Django 2.2.15 on 2020-08-25 14:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=4000)),
                ('type_question', models.IntegerField(choices=[(0, 'Ответ текстом'), (1, 'Выбрать ответ'), (2, 'Выбрать несколько вариантов')])),
            ],
            options={
                'db_table': 'questions',
            },
        ),
        migrations.CreateModel(
            name='QuestionResponse',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=200)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Question')),
            ],
            options={
                'db_table': 'questions_response',
            },
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=4000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
            ],
            options={
                'db_table': 'quizzes',
            },
        ),
        migrations.CreateModel(
            name='VisitorAnswer',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('answer', models.CharField(blank=True, default=None, max_length=1000, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Question')),
                ('question_variable_answer', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz.QuestionResponse')),
                ('visitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'visitor_answers',
            },
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Quiz'),
        ),
    ]
