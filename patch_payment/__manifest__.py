# -*- coding: utf-8 -*-
{
    'name': 'Patch Payments',
    'version': '1.0',
    'depends': ['pre_sales','payment'],
    'data': [
        'security/ir.model.access.csv',
        'views/patch_payment.xml',
        'data/sequence.xml',
    ],
    'installable': True,
}
