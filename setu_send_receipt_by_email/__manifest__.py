# -*- coding: utf-8 -*-
{
    'name': "Setu Send Receipt By Email",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'version': '18.0.0.0',
    'license': "LGPL-3",
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "http://www.setuconsulting.com",
    'category': 'Uncategorized',
    'depends': ['web', 'mail', 'website_sale',
                'accountant','setu_accounts_report_extended'],
    'data': [
        'views/report_bank_statement_line.xml',
        'views/account_move.xml',
        'views/account_payment_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'setu_send_receipt_by_email/static/src/**/*',
            'web/static/lib/jquery/jquery.js',
        ],
    },
}
