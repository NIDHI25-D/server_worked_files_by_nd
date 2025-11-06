# -*- encoding: utf-8 -*-
{
    'name': 'Identify Customers Exclusively Ey Delivery Method',
    'version': '18.0.0.0',
    'website': 'https://www.setuconsulting.com' ,
    'support': 'support@setuconsulting.com',
    'description': """Identify Customers Exclusively Ey Delivery Method""",
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'category': 'Delivery',
    'license': 'LGPL-3',
    'depends': [
        'sale', 'delivery','website_sale','contacts', 'point_of_sale', 'l10n_mx_edi_stock', 'setu_ecommerce_based', 'meli_oerp'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/shipping_carrier.xml',
        'views/delivery_carrier.xml',
        'views/website_sale_delivery.xml',
        'views/sale_order.xml',
        'views/res_partner_views.xml',
        'views/stock_picking.xml',
        'wizard/choose_delivery_carrier_views.xml',
        'views/report_cartaporte.xml',
    ],
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            'setu_prefered_delivery_methods/static/src/**/*',
        ],
    },
}
