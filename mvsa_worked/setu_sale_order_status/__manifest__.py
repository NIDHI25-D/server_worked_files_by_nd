# -*- coding: utf-8 -*-
{
    "name": "Sale Order Status",
    "summary": """The customers can see their sale order status """,
    "category": "Website",
    'version': '18.0.0.0',
    "author": "Setu Consulting Services Pvt. Ltd.",
    "license": "Other proprietary",
    "website": "https://www.setuconsulting.com",
    "description": """Shows sale order status""",
    "depends": ['portal', 'sale', 'setu_prefered_delivery_methods'],
    "data": [
        'views/sale_order_portal_template_extended.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'setu_sale_order_status/static/src/scss/sale_order_template_extended.scss',
        ],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
}
