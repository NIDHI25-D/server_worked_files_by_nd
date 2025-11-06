# -*- coding: utf-8 -*-
{
    'name': 'Setu Customer Lock',
    'version': '18.0.0.0',
    'category': 'Sales/Sales',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """Lock customer by specific reason to create sale order from website, POS and manually.""",
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'license': 'OPL-1',
    'depends': ['pos_sale', 'website_sale', 'repair'],
    'sequence': 24,
    'data': [
        'views/res_partner_category_views.xml',
        'views/templates.xml',
        'security/res_group.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'setu_customer_lock/static/src/js/screens.js',
        ],
        'web.assets_frontend': [
            '/setu_customer_lock/static/src/js/website_sale_update_quantity.js'
        ]
    },
}
