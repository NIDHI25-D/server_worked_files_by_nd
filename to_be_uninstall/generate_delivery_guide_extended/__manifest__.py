# -*- coding: utf-8 -*-
{
    'name': "generate_delivery_guide_extended",


    'description': """
        set system date for sign delidery document instead of done_date for the picking
    """,
    'license': 'LGPL-3',
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com/",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['l10n_mx_edi_stock'],

    # always loaded
    'data': [
        # 'views/fleet_vehicle_views.xml',
    ],
}
