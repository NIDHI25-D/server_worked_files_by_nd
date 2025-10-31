# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    # App information
    'name': 'Warehouse Efficiency Report',
    'version': '18.0.0.0',
    'category': 'Sale',
    'license': 'OPL-1',
    
    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    
    # Dependencies
    'depends': ['sale_marvelsa', 'stock_inv_ext'],
    
    # View
    'data': [
            'security/ir.model.access.csv',
            'views/picking_efficiency_report_views.xml',
            'views/warehouse_efficiency_report_views.xml',
            'views/stock_move.xml'
        ],

    # Technical        
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,
}
