# -*- coding: utf-8 -*-
{
    'name': "Location stock zero report",

    'summary': """
        Report showing stock location which has Zero Quantity.""",

    'description': """
        Report showing stock location which has Zero Quantity.
    """,
    'license': 'LGPL-3',
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/location_stock_zero_report.xml'
    ],
}
