# -*- coding: utf-8 -*-
{
    'name': "setu_purchase_automation",

    'summary': """ Make a Purchase Flow Automation """,

    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': "https://www.setuconsulting.com",
    'category': 'purchase',
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['purchase_stock', 'account', 'setu_l10n_mx_edi_extended'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_bank_statement_line.xml',
        'views/account_payment_term.xml',
        'views/purchase_order.xml',
        'views/custom_catelogs.xml',
        'views/custom_agency.xml',
        'views/purchase_carrier.xml',
        'views/product_template.xml',
        'views/loading_port_catelogues.xml',
        'views/res_partner.xml',
        'views/stock_picking.xml',
        'views/res_config_settings.xml',
        'views/purchase_order_line_view.xml',
        'views/preorder_forwarder.xml',
        'data/henco_api_cron.xml',
        'views/arrival_change_reason_view.xml',
    ],
}
