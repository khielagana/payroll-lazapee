# Generated by Django 5.0.6 on 2024-05-10 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll_app_v1', '0002_alter_employee_id_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='payslip',
            name='philhealth',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
