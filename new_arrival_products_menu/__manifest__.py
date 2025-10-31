# -*- encoding: utf-8 -*-
{
    'name': 'New Arrival Products Menu',
    'description': 'Add days filter new arrival product menu',
    'summary': """Add days filter new arrival product menu""",
    'author': 'Setu Consulting Pvt. Ltd.',
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'website': 'https://www.setuconsulting.com/',
    'category': 'website',
    'depends': ['website_sale','stock'],
    'data': [
        'data/new_arrivals_product_menu_data.xml',
        'views/res_config_settings_views.xml',
        'views/templates.xml'
    ],
}
