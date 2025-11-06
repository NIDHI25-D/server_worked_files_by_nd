# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    # App information
    'name': 'Setu Bbva Payment Acquirer',
    'version': '18.0.0.0',
    'category': 'Hidden',
    'license': 'OPL-1',

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',

    # Dependencies
    'depends': [ 'setu_payment_acqirers'],

    # View
    'data': ['security/ir.model.access.csv',
             'view/templates.xml',
             'view/payment_bbva_templates.xml',
             'data/payment_provider_data.xml',
             'view/payment_views.xml',
             'view/sale_order.xml'
             ],

    # Technical
    'installable': True,
    'auto_install': False,
    'application': False,
    'active': False,

}
