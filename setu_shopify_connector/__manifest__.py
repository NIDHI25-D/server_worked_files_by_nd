# -*- coding: utf-8 -*-

{
    # App information
    'name': 'Odoo Shopify Connector',
    'version': '1.2',
    'category': 'Sales',
    'license': 'OPL-1',

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',

    # Dependencies
    'depends': ['setu_ecommerce_based'],

    'summary': """ 
        Shopify odoo connector is an application that helps to integrate shopify online store with Odoo ERP. 
        Integrating Shopify store with Odoo ERP helps shopify seller to manage various functionalities of Shopify now directly from ERP which aids 	 not only to end users but also to the management team of shopify. 
        Managing various functionalities that shopify stores provides as a cloud based eCommerce platform through the most effective ERP 		
        management System helps shopify sellers to operate all the functionalities through ODOO ERP  provides the most user friendly environment.
        By using Shopify connector  various functionalities like importing products and its details, publishing products to Shopify, Importing 
        Orders to Odoo, and customer details, orders, stock details, reports, invoices, returns, refunds, point of Sale, Synchronize products, 
        manage multiple stores, manage Shopify payouts.
        shopify integration, shopify odoo integration, shopify return, shopify refund, odoo shopify refund, odoo shopify return, shopify risky 
        order, import shopify order, export shopify order, import stock, import location, import shipped orders, import unshipped orders,
        woocommerce connector, odoo woocommerce connector, connectors, ecommerce connector, shopify connector, woocommerce connector,
        shopify pos, shopify return exchange, refund, inventory management, inventory reports, 
        """,

    'description': """ 
        To manage various functionalities that shopify provides as a powerful e-Commerce platform, the need for the most effective ERP management 
        System that operates all transactions providing a user friendly environment is a must. 
        Odoo is the best and most famous Open source ERP management system providing excellent, all in one features - accounting, sales, inventory 
        management, manufacturing, marketing,  easiest app integration, most flexible for customization and interface.
        Hence we have developed all-in-one Shopify odoo connector - An Omni channel solution that integrates Odoo ERP and Shopify eCommerce to 
        manage various functionalities of Shopify which aids not only to end users but also to the management team of shopify. 
        By using this connector various functionalities like importing products and its details, customer details, orders, stock details, 
        reports,invoices, returns, refunds, point of Sale.
        """,

    'images': ['static/description/banner.gif'],
    'sequence': 30,

    # Views
    'data': ['security/setu_shopify_group_security.xml',
             'security/ir.model.access.csv',
             'views/setu_shopify_dashboard_views.xml',
             'views/setu_shopify_menu.xml',
             'views/setu_muti_ecommerece_connector.xml',
             'views/setu_shopify_product_template_views.xml',
             'views/setu_shopify_product_product_views.xml',
             'views/setu_shopify_product_image_views.xml',
             'views/setu_shopify_payment_gateway_views.xml',
             'views/setu_shopify_stock_location_views.xml',
             'views/setu_shopify_process_history_views.xml',
             'views/setu_shopify_sale_order_automation_views.xml',
             'views/setu_shopify_risky_order.xml',
             'views/sale_order_views_extended.xml',
             'views/res_partner_views_extended.xml',
             'views/stock_picking_views_extended.xml',
             'views/account_move_views_extended.xml',
             'views/account_journal_views_extended.xml',
             'views/product_template_views_extended.xml',

             'views/setu_shopify_sale_order_process_configuration_views.xml',
             'views/setu_ecommerce_customer_chain_views.xml',
             'views/setu_ecommerce_product_chain_views.xml',
             'views/setu_ecommerce_order_chain_views.xml',
             'views/setu_shopify_payment_report_views.xml',
             ],
    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,

    # Price
    'price': 159,
    'currency': 'EUR',
}
