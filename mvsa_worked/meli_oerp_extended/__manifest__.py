{
    'name': 'Meli Extended',
    'version': '18.0.0.1',
    'summary': 'Used for changes related to the partners invoice address and print shipment labels in mercadolibre '
               'orders.',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'license': "LGPL-3",
    'website': 'https://www.setuconsulting.com',
    'depends': ['meli_oerp', 'meli_oerp_stock', 'crm', 'hr', 'marvelsa_sepomex'],
    'data': [
        'security/security.xml',
        'views/company.xml',
        'views/orders.xml',
        'views/sale_order_view.xml',
        'views/shipment_view.xml',
        'views/stock_picking.xml',
    ],
    'installable': True,
    'auto_install': False
}
