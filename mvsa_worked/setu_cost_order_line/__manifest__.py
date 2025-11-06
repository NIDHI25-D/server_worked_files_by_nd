# -*- coding: utf-8 -*-
{
    'name': "Update Cost - Sale order line",
    'description': """Update Cost - Sale order line""",
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com",
    'category': 'stock',
    'depends': ['stock_account', 'sale_margin', 'mrp', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'report/account_invoice_report.xml',
        'wizard/sale_order_cost_change_wizard.xml',
        'views/sale_order_line.xml',
        'views/account_move_line.xml',
        'report/account_move.xml',
        'wizard/stock_picking_return_views.xml',
        'views/stock_location_views.xml'
    ],
    'application': True,
}