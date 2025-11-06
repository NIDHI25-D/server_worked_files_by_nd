# -*- coding: utf-8 -*-
{
    'name': "Setu Picking Control By Pallets",

    'summary': """
        Identify Put in pack as a Bundle or Pallets or Box type with print labelling""",
    'version': '0.1',
    'license': 'LGPL-3',
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com",
    'category': 'Sales',
    # any module necessary for this one to work correctly
    'depends': ['sale', 'stock_delivery', 'stock_barcode', 'marvelfields', 'stock_inv_ext'],

    'data': [
        'security/ir.model.access.csv',
        'views/stock_quant_views.xml',
        'report/report_package_barcode.xml',
        'wizards/put_in_pack_package_type_wizard.xml',
        'views/stock_picking.xml',
        'report/stock_package_views.xml',
        'report/parcel_tracking_report.xml',
        'views/templates.xml',
        'views/product_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'setu_picking_control_by_pallets/static/src/models/barcode_model_massive.js',
            'setu_picking_control_by_pallets/static/src/xml/templates.xml'
        ],
    },
}
