# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    # App information
    'name': 'Payment Acquirer Extended',
    'version': '18.0.0.1',
    'category': 'Hidden',
    'license': 'OPL-1',

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',

    # Dependencies
    'depends': ['portal','website_sale','account_payment','delivery', 'payment_stripe', 'setu_payment_voucher_planification_activity_automate'],

    # View
    'data': [
        'views/templates.xml',
        'security/ir.model.access.csv',
        'views/payment_provider_view.xml',
        'views/sale_order.xml'

    ],
    'assets': {
        'web.assets_frontend': [
            'setu_payment_acqirers/static/src/js/payment_form.js',
        ],
    },

    # Technical
    'installable': True,
    'auto_install': False,
    'application': False,
    'active': False,

}
