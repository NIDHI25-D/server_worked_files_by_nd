# -*- coding: utf-8 -*-

{
    # App information
    'name': 'Transport Management Extended',
    'version': '18.0.0.0',
    'category': 'Sales/Sales',
    'license': 'OPL-1',

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',

    # Dependencies
    'depends': ['transport_management', 'setu_picking_control_by_pallets', 'setu_sales_time_dashboard'],

    # Views
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/transport_shipment_views.xml',
        'views/transport_route_search_view.xml',
        'wizard/create_tms_shipment_wiz_view.xml'
    ],

    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,
}
