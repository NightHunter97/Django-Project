# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-25 08:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='attorney',
            field=models.BooleanField(default=False, verbose_name='Financial Power of Attorney'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Birth Date'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='card_number',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Identity Card Number'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='card_type',
            field=models.CharField(blank=True, choices=[('CHI', 'Child'), ('SPO', 'Spouse'), ('B/S', 'Brother/sister'), ('PAR', 'Parent')], max_length=7, null=True, verbose_name='Identity Card Type'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='document_type',
            field=models.CharField(blank=True, choices=[('B_ID', 'Belgian identity card'), ('B_FN', 'Belgian card of foreign resident'), ('FN_ID', 'Foreign identity card')], max_length=7, null=True, verbose_name='Identity Document Type'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='email',
            field=models.EmailField(blank=True, max_length=128, null=True, verbose_name='E-mail Address'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='foreign_register',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Foreign Register'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='full_name',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Full name'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='gender',
            field=models.CharField(blank=True, choices=[('F', 'Female'), ('I', 'Indeterminate'), ('M', 'Male')], db_index=True, max_length=7, null=True, verbose_name='Gender'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='general_practitioner',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='General Practitioner'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='language',
            field=models.CharField(blank=True, choices=[('E', 'English'), ('C', 'Chinese'), ('G', 'German'), ('S', 'Spanish'), ('I', 'Italian'), ('J', 'Japanise'), ('D', 'Dutch)')], max_length=7, null=True, verbose_name='Language'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='marital_status',
            field=models.CharField(blank=True, choices=[('SI', 'Single'), ('D', 'Divorced'), ('H', 'Co-habitant'), ('U', 'Unknown'), ('SE', 'Separated'), ('W', 'Widowed')], max_length=7, null=True, verbose_name='Marital Status'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='national_register',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='National Register'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='nationality',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Nationality'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='partner_name',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name="Partner's Name"),
        ),
        migrations.AlterField(
            model_name='patient',
            name='phone_number',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='post_code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Post Code'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='regional_recognition',
            field=models.BooleanField(default=False, verbose_name='Regional Disability Recognition'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='religion',
            field=models.CharField(blank=True, choices=[('ADV', 'Adventist'), ('AOG', 'Assembly of God'), ('BAP', 'Baptist'), ('BUD', 'Buddhist'), ('CAT', 'Catolic'), ('JSH', "Jehovan's Witness"), ('LUT', 'Lutheran'), ('MRN', 'Mormon'), ('NO', 'None'), ('ORT', 'Orthodox'), ('OTH', 'Other'), ('OTH', 'Other'), ('PST', 'Protestant'), ('QUA', 'Quaker')], max_length=7, null=True, verbose_name='Religion'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='status',
            field=models.CharField(blank=True, choices=[('PR', 'Present'), ('TEMP', 'Temporary released')], max_length=7, null=True, verbose_name='Status'),
        ),
    ]
