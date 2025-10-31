# -*- coding: utf-8 -*-
{
    'name': "Sale Order from Multiple Warehouses",
    'description': """
        This module create sale orders from multiple warehouses 
        when the stcok in the warehouse not complete the sale order
    """,
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com",
    'category': 'sale',
    'depends': ['sale_management','website_sale_stock',],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_warehouse.xml',
        'views/sale_order.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'sale_order_multi_warehouse/static/src/components/**/*',
        ],

    },

}
