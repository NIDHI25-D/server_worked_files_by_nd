# -*- coding: utf-8 -*-
{
    # App information
    "name": "Mass Editing",
    "version": "18.0.1.0.0",
    "category": "Base",
    'license': 'AGPL-3',
    "summary": """ This module allow to mass editing in list and form view for every model.""",

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """This module allow to mass editing in list and form view for every model.""",


    # Dependencies
    "depends": ["base"],

    # View
    "data": [
        "security/ir.model.access.csv",
        "views/ir_actions_server.xml",
        "wizard/mass_editing_wizard.xml",
    ],

    # Assests
    "assets": {
        "web.assets_backend": [
            "/mass_editing/static/src/js/record.esm.js",
            "/mass_editing/static/src/js/static_list.esm.js",
        ]
    },
    "demo": ["demo/mass_editing.xml"],
    "external_dependencies": {"python": ["openupgradelib"]},
    # "pre_init_hook": "pre_init_hook",

    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,
}
