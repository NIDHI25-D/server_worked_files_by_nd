# -*- coding: utf-8 -*-
{
    'name': 'Setu login as any user',
    'version': '16.0',
    'sequence': 6,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'license': 'LGPL-3',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'summary': " ",
    'description': """ Used for login as any user without changing the password. """,
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/login_activity.xml',
    ],
    'qweb': [],
    'assets': {
        'web.assets_backend': [
            'setu_login_as_any_user/static/src/js/open_wizard.js',
            'setu_login_as_any_user/static/src/xml/header.xml',
        ],
    },
}

