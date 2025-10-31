# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    # App information
    'name': 'Stock Inventory Extended',
    'version': '18.0.0.0',
    'category': 'Inventory',
    'license': 'OPL-1',

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',

    # Dependencies
    'depends': ['stock_barcode', 'l10n_mx_edi_landing', 'setu_urgent_order_enhancement', 'sale_crm', 'website_sale_stock', 'marvelfields', 'product_brand', 'marvelmarcas'],#b'coz of product_brand includes stock_account,

    # View
    'data': [
        'security/stock_inventory_discrepancy_security.xml',
        'security/ir.model.access.csv',
        'views/stock_move_line_view.xml',
        'views/stock_quant_view.xml',
        'views/stock_landed_cost.xml',
        'views/account_report_extended.xml',
        'views/stock_picking.xml',
        'views/stock_picking_barcode_views.xml',
        'views/stock_valuation_menu_inherit_for_add_group.xml',
        'views/delivery_slip_report_inherited.xml',
        'views/unspsc_code_id_add_field.xml',
        'views/order_fill_error_picking.xml',
        'views/purchase_order_views.xml',
        'wizard/show_popup.xml',
        'wizard/wizard_cancel_reason.xml',
        'views/order_fill_error_catalog_view.xml',
        'views/sale_order_view.xml',
        'views/product_template_view.xml',
    ],

    'assets': {
        'web.assets_backend': [
            '/stock_inv_ext/static/src/js/InventoryClientAction.js',
            '/stock_inv_ext/static/src/xml/barcode_template.xml',
        ],
    },

    # Technical
    'installable': True,
    'auto_install': False,
    'application': False,
    'active': False,

}
