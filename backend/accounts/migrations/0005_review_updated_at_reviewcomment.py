# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_rename_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ReviewComment',
            fields=[
                ('comment_id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField(help_text='The comment text')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(help_text='The user who wrote this comment (service owner or moderator)', on_delete=django.db.models.deletion.CASCADE, related_name='review_comments', to=settings.AUTH_USER_MODEL)),
                ('review', models.ForeignKey(help_text='The review this comment is attached to', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='accounts.review')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]