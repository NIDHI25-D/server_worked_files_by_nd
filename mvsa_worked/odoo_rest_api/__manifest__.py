# -*- coding: utf-8 -*-
{
    'name': 'Setu Odoo Rest API',
    'version': '1.0',
    'summary': 'Rest API Odoo',
    'sequence': 40,
    'description': """Rest API Odoo""",
    'license': 'AGPL-3', # Deja solo una licencia (esta o la que prefieras)
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com', # Deja solo un website (este o el que prefieras)
    'depends': ['base_setup', 'l10n_mx_edi','sale'],
    'data': [
        # views
        'views/res_config_settings.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False, # Si quieres que aparezca en la pantalla principal de Apps, cámbialo a True
    'auto_install': False,
}