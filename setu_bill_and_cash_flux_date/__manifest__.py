# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Setu Bill and Cash Flux Date',
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'category': 'purchase',
    'summary': """Auto create bill withing the billing type""",
    'website': 'http://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """
        Auto Create vendor bill based on billing type.
    """,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'sequence': 20,
    'depends': ['setu_purchase_automation', 'setu_accounts_report_extended'],
    'data': [
        'security/ir.model.access.csv',
        'views/bill_type.xml',
        'views/payment_term.xml',
        'views/purchase_order.xml',
        'views/res_partner_category.xml',
    ],
    'application': True,
}
