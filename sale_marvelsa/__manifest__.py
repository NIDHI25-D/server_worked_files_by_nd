# -*- coding: utf-8 -*-
{
    'name': "Custom module for Sales Marvelsa",
    'description': """
        Custom module for sales Marvelsa
    """,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'license': 'LGPL-3',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sales',
    'version': '18.0.0.0',
    'depends': ['setu_sales_time_dashboard', 'portal', 'contacts','sale_loyalty','setu_urgent_order_enhancement', 'marvelsa_sepomex', 'sale_amazon', 'limite', 'setu_cfdi_and_payment_way', 'setu_ecommerce_based', 'meli_oerp'],
    # always loaded
    'data': [
        'security/security.xml',
        'views/sale_order.xml',
        'views/traffic.xml',
        'views/stock_picking.xml',
        'views/price_list_view.xml',
        'views/res_config_settings.xml',
        'views/website.xml',
        'views/res_partner.xml',
        'views/stock_move.xml',
        'views/portal_template_inherit.xml',
        'data/email_template.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'views/legal_person.xml',
        'views/product_template.xml',
        'views/account_move.xml',
        'views/templates.xml',
        'views/product_tag.xml',
        'views/delivery_carrier.xml',
        'report/sale_order.xml',
        'report/account_move.xml',
        'views/stock_picking_type.xml',
        'wizard/prepare_picking.xml',
    ],
'assets': {
        'web.assets_frontend': [
            "sale_marvelsa/static/src/js/checkout.js",
        ]
    },
}