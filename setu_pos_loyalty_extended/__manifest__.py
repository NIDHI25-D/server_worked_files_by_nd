# -*- coding: utf-8 -*-
{
    'name': 'Setu POS Loyalty Extended',
    'version': '18.0',
    'category': 'Point Of Sale',
    'license': 'LGPL-3',
    'summary': """""",
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """""",
    'author': 'Setu Consulting Services Pvt. Ltd.',
    # 'depends': ['pos_loyalty', 'sale', 'account'],
    'depends': ['point_of_sale'],
    'data': [
        # 'views/pos_config.xml',
        # 'views/assets.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'setu_pos_loyalty_extended/static/src/js/*.js',
        ],
    },
    'application': False,
}
