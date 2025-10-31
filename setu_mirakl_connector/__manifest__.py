# -*- coding: utf-8 -*-

{
    # App information
    'name': 'Setu Odoo Mirakl Connector',
    'version': '18.0.0.0',
    'category': 'Sales',
    'license': 'OPL-1',
    'price': 159,
    'currency': 'MXN',

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',

    # Dependencies
    'depends': ['base','setu_ecommerce_based'],

    'summary': """ 
                Mirakl is the leading technology partner to drive digital growth.
                Mirakl connects you to the largest curated network of top-tier sellers and partners, accelerating your eCommerce growth.
               """,

    'description': """ 
                    Mirakl Connecrtor imports the Sale order as well as creates the partners in the Odoo from the Coppel Marketplace.
                   """,

    # Views
    'data': [
        'security/setu_mirakl_group_security.xml',
        'security/ir.model.access.csv',
        'security/mirakl_order_status_data.xml',
        'views/setu_mirakl_dashboard_views.xml',
        'views/setu_mirakl_main_menu.xml',
        'views/setu_multi_ecommerce_connector.xml',
        'views/setu_mirakl_payment_gateway.xml',
        'views/setu_mirakl_sale_order_automation_views.xml',
        'views/sale_order.xml',
        'views/setu_mirakl_process_history_views.xml',
        'views/setu_mirakl_process_history_line_views.xml',
        'views/res_partner.xml',
        'views/account_move.xml',
        'wizard_views/setu_cron_configuration_wiz_views.xml',
        'wizard_views/setu_mirakl_import_export_process_wiz_views.xml'
    ],

    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,
}