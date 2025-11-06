# -*- coding: utf-8 -*-
{
    # App Information
    'name': "Setu Payment Voucher Planification Activity Automate",
    'category': 'Sales',
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'summary': """
        Set automatically activity to the users sale orders according to the pricelist selected  during the pricelist """,
    "description": """
        Set automatically activity to the users sale orders according to the pricelist selected  during the pricelist """,

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'maintainer': 'Setu Consulting Services Private Limited',
    'website': "https://www.setuconsulting.com",

    # Dependencies
    'depends': ['portal','website_sale','marvelfields'],

    # Views
    'data': [
        'views/product_pricelist_views.xml',
        'views/payment_provider_views.xml',
        'views/sale_order_views.xml',
        'views/templates.xml',
        'views/sale_portal_templates.xml',
        'views/account_portal_templates.xml',
        'views/account_move_views.xml',
    ],

    #Assets
    'assets': {
        'web.assets_frontend': [
            'setu_payment_voucher_planification_activity_automate/static/src/js/main.js',
        ],
    },

    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,

}
