# -*- coding: utf-8 -*-
{
    'name': ' Cookie - Consent Manager Basic',
    'summary': 'Manage consent for google analytics and essential cookies',
    'version': '18.0.0.0',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'support': 'support@setuconsulting.com',
    'website': 'https://www.setuconsulting.com',
    'category': 'Website',
    'price': 49.00,
    'currency': 'EUR',

    'depends': ['website'],

    'data': [
        'views/res_config_settings_views.xml',
        'views/website_layout.xml'
    ],
    'assets': {
        'web.assets_frontend_minimal': [
            'manatec_consent_manager_basic/static/src/js/klaro.config.js',
            'manatec_consent_manager_basic/static/src/js/klaro.js',
        ],
    },

    'description': 'Manage consent for google analytics and essential cookies',
    'images': ['static/description/thumbnail.png'],
    'license': 'OPL-1',
}
