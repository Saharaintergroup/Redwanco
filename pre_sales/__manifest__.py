# -*- coding: utf-8 -*-
{
        'name': 'Pre-Sales',
        'version': '12.0.1.0.10',
        'summary': 'Pre-Sales Management',
        'category': 'Sale',
        'author': 'Vinaya S B',
        'maintainer': 'Cybrosys Techno Solutions',
        'company': 'Cybrosys Techno Solutions',
        'website': 'https://www.cybrosys.com',
        'depends': ['base', 'contacts', 'sale', 'account', 'stock'],
        'data': ['security/ir.model.access.csv',
                'views/pre_sale.xml'
        ],
        'images': ['static/description/icon.png'],
        'license': 'AGPL-3',
        'installable': True,
        'application': False,
        'auto_install': False,
}
