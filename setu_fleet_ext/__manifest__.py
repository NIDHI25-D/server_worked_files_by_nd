# -*- coding: utf-8 -*-
{
    'name': "Fleet Management Extended",
    'description': """Fleet Management Extended""",
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com",
    'category': 'Fleet',
    'depends': ['fleet', 'l10n_mx_edi_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_views.xml',
        'views/combustible_card_type.xml',
        'views/combustible_pin_type.xml',
        'views/pase.xml',
    ],
}
