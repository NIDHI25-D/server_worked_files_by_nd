# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Auto Create Sale Order Invoice',
    'version': '16.0.1',
    'category': 'stock',
    'summary': """Auto Create sale order invoice after validating the delivery order""",
    'website': 'http://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """
        Auto Create sale order invoice after validating the delivery order
    """,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'license': 'OPL-1',
    'sequence': 20,
    'depends': ['sale_stock', 'l10n_mx_edi', 'account_edi','marvelfields'],
    'data': [
        'views/res_config_settings.xml',
        # 'views/account_journal.xml',
        # 'views/account_account.xml',
        'views/sale_order.xml',
        'views/account_payment_term.xml',
        # 'views/product_pricelist.xml', remove due to not usage
        'views/res_partner_ext.xml',
        'data/create_invoice_cron.xml',
        'data/cancel_sale_order_cron.xml',
        'data/cancel_invoice_cron.xml',
        'data/cancel_sale_order_automatically_cron.xml',
        'data/edi_sign_invoice_payments.xml'

    ],
    'application': True,
}