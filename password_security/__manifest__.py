# -*- coding: utf-8 -*-
{
    # App information
    "name": "Password Security",
    "version": "18.0.0.0",
    "category": "Base",
    'license': 'OPL-1',
    "summary": """ Allow admin to set password security requirements.""",

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """for Allow admin to set password security requirements.""",

    # Dependencies
    "depends": ["auth_signup", "auth_password_policy_signup"],

    # View
    "data": [
        "views/res_config_settings_views.xml",
        "security/ir.model.access.csv",
        "security/res_users_pass_history.xml",
        "views/auth_signup_reset_templates.xml",
    ],

    # Demo Data
    "demo": [
        "demo/res_users.xml",
    ],

    "assets": {
        'web.assets_frontend': [
            'password_security/static/src/js/extended_meter.js',
        ],
    },

    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,
}
