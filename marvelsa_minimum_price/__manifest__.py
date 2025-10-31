# -*- encoding: utf-8 -*-
{
    'name': "SGEEDE Minimum Price Module",
    'summary': """Lock and control your minimum sale price to POS, Sales Order and Invoice""",
    'description': """Lock and control your minimum sale price to POS, Sales Order and Invoice""",
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com",
    'category': 'Tools',
    'depends': ['point_of_sale', 'setu_discount_and_loyalty_enhancment'],
    'data': [
        'views/product_template_views.xml',
        'views/product_category_views.xml',
        'views/point_of_sale.xml',
        'views/res_config_extended.xml',
        'views/account_move.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'marvelsa_minimum_price/static/src/**/*',
        ],
    },
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'active': False,
    'price': 9.99,
    'currency': "EUR",

    'images': ['images/main_screenshot.png',
               'images/sgeede.png'],
}
