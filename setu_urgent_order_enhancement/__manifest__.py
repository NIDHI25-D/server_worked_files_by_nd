# -*- coding: utf-8 -*-
{
    'name': "Setu Urgent Order Enhancement",
    'summary': """
        Enhancement of Urgent order process""",
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'license': 'LGPL-3',
    'category': 'sale',
    'version': '18.0.0.0',
    'depends': ['sale', 'crm', 'stock', 'pos_sale'],
    'data': [
        'security/security.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
    ],
}
