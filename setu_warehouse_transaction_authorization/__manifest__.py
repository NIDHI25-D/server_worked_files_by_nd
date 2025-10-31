# -*- encoding: utf-8 -*-
{
    'name': 'Warehouse Transfer Authorization',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'website': 'https://www.setuconsulting.com',
    'category': 'Inventory',
    'depends': ['stock','stock_inv_ext'],
    'data': [
        'security/ir.model.access.csv',
        'views/warehouse_authorization.xml',
        'views/stock_location.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
