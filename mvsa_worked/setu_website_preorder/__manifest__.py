{
    "name": "Website Pre-Order",
    "summary": """The customers can place pre-orders for the selected products on the Odoo 
    website which are out of 
    stock.""",
    "category": "Website",
    "version": "18.0.0.0",
    "sequence": 1,
    "author": "Setu Consulting Services Pvt. Ltd.",
    "license": "Other proprietary",
    "website": "https://www.setuconsulting.com",
    "description": """Odoo Website Pre-Order
                            Place pre-orders on website Pre orders on odoo Advanced orders on 
                            website Odoo pre orders Odoo website advanced orders
                            Order out of stock product Out of stock orders Odoo back orders 
                            Website backorders""",
    "depends": ['purchase', 'website_sale_stock','setu_price_update', 'sale_marvelsa','sale_loyalty','stock_inv_ext', 'product_brand', 'queue_job'],#'website_sale_delivery',
    "data": [
        'security/ir.model.access.csv',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/res_config_setting.xml',
        'views/templates.xml',
        'views/product_template.xml',
        'views/product_product.xml',
        'views/stock_picking.xml',
        'views/account_move.xml',
        'views/delivery_carrier.xml',
        'wizard/purchase_order_confirm_wizard.xml',
        'data/presale_price_cron.xml',
        'data/calculate_minimum_qty.xml',
        'data/sale_order_update_channel_data.xml'
    ],
    "demo": [],
    'assets': {
        'web.assets_frontend': [
            'setu_website_preorder/static/src/**/*',
        ],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
}
