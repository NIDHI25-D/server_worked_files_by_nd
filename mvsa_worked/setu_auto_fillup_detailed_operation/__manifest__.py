# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Setu Auto Fillup Detailed Operation',
    'version': '18.0.0.0',
    'category': 'stock',
    'license': 'LGPL-3',
    'summary': """
            This module is used to create records of the products in Transfer, which are mentioned in the csv file
    """,
    'description': """
            This module is used to create records of the products in Transfer, which are mentioned in the csv file.
     """,
    'author': 'Setu Consulting Services Pvt. Ltd.',

    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'depends': ['base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/auto_fill_up_operation_line.xml',
    ],
}
