# -*- coding: utf-8 -*-
{
    'name': 'Sales Time Dashboard',
    'version': '18.0.0.0',
    'category': 'sale',
    'summary': """This module is used to create data of sales 
                   i.e - time difference between create date - confirmation date and other difference of sale flow till invoice validation.""",
    'website': 'http://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """This module is used to create data of sales 
                   i.e - time difference between create date - confirmation date and other difference of sale flow till invoice validation.""",
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'license': 'LGPL-3',
    'depends': ['sale_stock', 'resource','sale_order_multi_warehouse', 'hr', 'setu_cost_order_line', 'marvelfields', 'meli_oerp'],
    'data': [
        'security/sales_time_dashboard_group.xml',
        'security/ir.model.access.csv',
        'views/sales_time_dashboard_view.xml',
        'views/sale_order_view.xml',
        'views/stock_picking_view.xml',
        'views/resource_calendar_view.xml',
        'db_function/get_sales_time_data.sql',
    ],
    'assets': {
        'web.assets_backend': [
            'setu_sales_time_dashboard/static/src/datetime_picker.js'
        ],
    },
    'application': False,
    'installable': True,
}

