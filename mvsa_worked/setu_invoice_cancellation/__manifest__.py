# -*- coding: utf-8 -*-
{
    'name': "setu invoice cancellation",

    'summary': """ Used for knowing the why customer cancels the invoice """,

    'description': """ """,

    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com",

    # for the full list
    'category': 'Accounting',
    'version': '18.0.0.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account_edi', 'l10n_mx_edi', 'accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_move.xml',
        'views/setu_invoice_cancel.xml',
        'wizard/account_move_reversal.xml',
        'wizard/l10n_mx_edi_invoice_cancel_view.xml',
    ],
}
