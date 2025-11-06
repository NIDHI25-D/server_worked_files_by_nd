# -*- coding: utf-8 -*-
{
    'name': "Setu Assets Module Enhancement",

    'summary': """ Show the other information in Accounting Assets. """,

    'description': """
        Show the other information in Accounting Assets.
    """,
    'license': "LGPL-3",
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "http://www.setuconsulting.com",

    'category': 'Uncategorized',
    'version': '18.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'account_asset', 'accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/ram_memory_type.xml',
        'views/ram_memory_capacity.xml',
        'views/processor_speed.xml',
        'views/processor_model.xml',
        'views/processor_generation.xml',
        'views/operative_system_version.xml',
        'views/operative_system_type.xml',
        'views/operative_system_distribution.xml',
        'views/network_card_type.xml',
        'views/network_card_mac_address.xml',
        'views/hard_disk_type.xml',
        'views/hard_disk_capacity.xml',
        'views/account_asset.xml',
        'views/assets_menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
