# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    # App information
    'name': 'Setu Shopify Connector Extended',
    'version': '1.2',
    'category': 'Sales',
    'license': 'OPL-1',

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',

    # Dependencies
    'depends': ['setu_shopify_connector'],

    # Views
    'data': ['views/setu_multi_ecommerce_connector_extended.xml',
                 'views/setu_multi_ecommerce_connector_inherit.xml',
             ],

    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,
}
