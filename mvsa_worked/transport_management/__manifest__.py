# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
{
    'name': "Sales Transport Management | Shipping Management | Freight Management | Transport Management | Courier Management",
    'summary': """Sales Transport Management, Shipment Management & Freight Management""",
    'description': """
       - Sales Transport Management
       - Sales Shipping Management
       - Transport Management
       - Freight Management
       - Delivery Order Management
       - Courier Management
    """,
    'category': 'Sales/Sales',
    'version': '1.3',
    'author': 'TechKhedut Inc.',
    'company': 'TechKhedut Inc.',
    'category': 'Industry',
    'maintainer': 'TechKhedut Inc.',
    'website': "https://www.techkhedut.com",
    'depends': [
        'mail',
        'contacts',
        'fleet',
        'sale_management',
        'stock',
    ],
    'data': [
        # Data
        'data/sequence.xml',
        'data/data.xml',
        'data/shipping_order_details_mail.xml',
        # Security
        'security/groups.xml',
        'security/ir.model.access.csv',
        # Wizard
        'wizard/ship_order_views.xml',
        'wizard/shipment_reschedule.xml',
        # Views
        'views/transporter_views.xml',
        'views/delivery_type_views.xml',
        'views/transport_location_views.xml',
        'views/transport_route_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/res_partner_views.xml',
        'views/shipment_operation_views.xml',
        'views/transport_shipment_views.xml',
        'views/stock_picking_views.xml',
        'views/transport_delivery_order_views.xml',
        'views/sale_order.xml',
        # Reports
        'report/delivery_order.xml',
        # Templates
        'views/assets.xml',
        # Menu
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'transport_management/static/src/xml/template.xml',
            'transport_management/static/src/scss/style.scss',
            'transport_management/static/src/js/lib/apexcharts.js',
            'transport_management/static/src/js/shipment.js',
        ],
    },
    'images': ['static/description/shipment-management.gif'],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 42.0,
    'currency': 'USD',
}
