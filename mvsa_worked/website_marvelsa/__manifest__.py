# -*- coding: utf-8 -*-
{
    'name': "Custom Website Sale module for Marvelsa Company",
    'description': """
        Show the spare parts of article on website product detail
    """,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'license': 'LGPL-3',
    'category': 'website',
    'version': '18.0.0.0',
    'depends': ['base','website_sale','mrp'],
    'data': [
    	'security/ir.model.access.csv',
        'data/schedule_data.xml',
        'views/res_config_setting.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/res_partner.xml',
    ],
}
