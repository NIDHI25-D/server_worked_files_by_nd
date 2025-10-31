# -*- coding: utf-8 -*-
{
    "name": "POS Stock",
    "summary": """The user can display the product quantities on the Odoo POS with the module. If set, 
                  The user cannot add out of stock products to the POS cart.""",
    "category": "Point of Sale",
    "version": "18.0.0.0",
    "sequence": 1,
    "author": "Setu Consulting Services Pvt. Ltd.",
    "license": "Other proprietary",
    "website": "https://www.setuconsulting.com",
    "description": """Odoo POS Stock
                        Show product quantity in POS
                        Out of stock products
                        Out-of-stock products POS
                        Added product quantities
                        POS product stock
                        Show stock pos
                        Manage POS stock
                        Product management POS""",
    "depends": ['point_of_sale', 'loyalty', 'account'],
    "data": [
        'views/res_config_settings.xml',
        'views/res_partner_view.xml',
    ],

    'assets': {
        'point_of_sale._assets_pos': [
            'pos_stocks/static/src/**/*',
        ],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
}
