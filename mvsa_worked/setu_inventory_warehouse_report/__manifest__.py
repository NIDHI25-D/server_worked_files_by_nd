{
    'name': 'Product Warehouse Report',
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'depends': ['stock', 'product_brand', 'setu_price_update', 'marvelfields'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/inventory_warehouse_report_views.xml',
        'db_function/set_inventoy_warehouse_wise_report.sql'
    ],
    'installable': True,
    'auto_install': False
}