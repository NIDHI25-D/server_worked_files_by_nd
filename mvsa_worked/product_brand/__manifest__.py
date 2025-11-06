{
    'name': 'Product Brand Manager',
    'version': '18.0.0.0',
    'development_status': "Mature",
    'category': 'Product',
    "author": "Setu Consulting Services Pvt. Ltd.",
    "license": "Other proprietary",
    "website": "https://www.setuconsulting.com",
    'summary': "Product Brand Manager",
    'license': 'AGPL-3',
    'depends': ['setu_cost_order_line'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/product_brand_view.xml',
        'views/sale_order.xml',
        'views/product_product.xml',
        'views/sale_report_search.xml',
        'reports/sale_report_view.xml',
        'reports/account_invoice_report_view.xml',
    ],

    'installable': True,
    'auto_install': False
}
