# -*- coding: utf-8 -*-
{
        'name': 'Inventory Extended for Presale',
        'version': '12.0.1.0.11',
        'summary': 'Inventory Extended for Presales Management',
        'category': 'Sale',
        'author': 'Vinaya S B',
        'maintainer': 'Cybrosys Techno Solutions',
        'company': 'Cybrosys Techno Solutions',
        'website': 'https://www.cybrosys.com',
        'depends': ['pre_sales', 'pre_sales_extended'],
        'data': [
                 'views/pre_sale_delivery.xml',
                 'report/delivery_report.xml',
                 'report/packing_template.xml',
                 'report/packing_label.xml',
                 'report/send_out_order.xml',
                 'report/send_out_order_view.xml',
                 'views/send_out_form_extend.xml',
                 'security/ir.model.access.csv'
        ],
        'images': [],
        'license': 'AGPL-3',
        'installable': True,
        'application': False,
        'auto_install': False,
}
