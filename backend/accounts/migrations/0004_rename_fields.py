# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_review'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='service_id',
            new_name='service',
        ),
        migrations.RenameField(
            model_name='review',
            old_name='user_id',
            new_name='user',
        ),
    ]