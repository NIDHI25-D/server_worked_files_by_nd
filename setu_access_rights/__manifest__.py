# -*- coding: utf-8 -*-
{
    'name': "Setu Access Rights",
    'summary': "Access Rights Related Changes",
    'description': """
        Access rights related changes
    """,
    'author': "Setu Consulting Services Pvt. Ltd.",
    'license': "LGPL-3",
    'website': "https://www.setuconsulting.com",
    'category': 'Extra tools',
    'version': '18.0.0.0',
    'depends': ['mail', 'web'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/view_setu_access_rights.xml',
    ],
}
