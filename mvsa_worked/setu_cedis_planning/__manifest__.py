# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Setu Cedis Planning',
    'version': '18.0',
    'category': 'stock',
    'license': 'LGPL-3',
    'summary': """
    """,
    'description': """
            Auto fill cedis planning in transfer.
     """,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'depends': ['base', 'stock', 'stock_inv_ext', 'sale_marvelsa'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_warehouse.xml',
    ],
}
