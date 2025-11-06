# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Associate Pos Invoice TO Bank Statements',
    'version': '18.0.0.0',
    'category': 'sale',

    'author': 'Setu Consulting Services Pvt. Ltd.',
    'support': 'support@setuconsulting.com',
    'website': 'https://www.setuconsulting.com',

    'summary': """associate invoices of pos with bank statements""",
    'description': """This module are used for POS invoices in respected Bank Reconciliation.""",
    'license': 'OPL-1',
    'sequence': 25,
    'depends': ['account', 'point_of_sale', 'l10n_mx_edi'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_bank_statement_line.xml',
        'views/associate_pos_invoice_to_bank_statement_view.xml',
        'views/account_move.xml'

    ],
    'application': True,
    'assets': {
            'web.assets_backend': [
                'associate_pos_invoices_to_bank_statement/static/src/components/**/*',
            ],
        }
}
