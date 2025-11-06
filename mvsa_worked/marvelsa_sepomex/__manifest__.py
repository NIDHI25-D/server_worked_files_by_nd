# -*- encoding: utf-8 -*-
{
    'name': "Sepomex",
    'description': """
        Record the colonies by postal code based on SEPOMEX catalog
    """,
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com",
    'support': 'support@setuconsulting.com',
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'base',
    # any module necessary for this one to work correctly
    'depends': ['base','contacts','l10n_mx_edi_extended','base_address_extended'],
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_colony.xml',
        'views/res_partner.xml',
    ],
    'post_init_hook': 'post_init_hook',
}