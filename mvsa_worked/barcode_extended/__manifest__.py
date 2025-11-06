# -*- encoding: utf-8 -*-
{
    'name': 'Setu Barcode Extended',
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com",
    'depends': ['stock_barcode'],

    'assets': {
        'web.assets_backend': [
            'barcode_extended/static/src/models/*.js',
            'barcode_extended/static/src/xml/*.xml',
        ],
    },
}