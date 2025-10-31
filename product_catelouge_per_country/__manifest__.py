# -*- coding: utf-8 -*-
{
    # App information
    'name': 'Setu Product Per Country',
    'summary': """Products display as per the user country""",
    'version': '18.0.0.0',
    'license': "LGPL-3",

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com/',
    'support': 'support@setuconsulting.com',
    'description': """Products display as per the user country""",

    # Dependencies
    'depends': ['product_brand',
                'setu_abc_analysis_reports_extended',
                'new_arrival_products_menu',
                'marvelfields'],

    # View
    'data': [
        'views/product_template_views.xml',
        'views/website_template_views.xml',
    ],

    # Assets
    'assets': {
        'web.assets_frontend': [
            'product_catelouge_per_country/static/src/js/website_template.js'
        ],
    },

    # Technical
    'application': True,
    'installable': True,
    'auto_install': False,
    'active': False,
}
