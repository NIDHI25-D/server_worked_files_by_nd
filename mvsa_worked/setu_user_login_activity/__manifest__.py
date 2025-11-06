# -*- coding: utf-8 -*-
{
    'name': "Setu User Login Activity",
    'description': """Setu User Login Activity""",
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com",
    'depends': ['base', 'website'],
    'data': [
        'security/user_login_activity_group.xml',
        'security/ir.model.access.csv',
        'views/user_login_activity.xml',
    ]
}