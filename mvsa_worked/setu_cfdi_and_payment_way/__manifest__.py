# -*- coding: utf-8 -*-
{
    'name': 'CFDI and payment Way',
    'version': '18.0.0.0',
    'category': 'sale',
    'license': 'LGPL-3',
    'sequence': 20,
    'summary': """CFDI and payment Way""",

    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description':
        """
           A CFDI (Comprobante Fiscal Digital por Internet) is an electronic invoicing system used in Mexico for tax
           compliance, regulated by the SAT (Servicio de Administración Tributaria). The Payment Way (Forma de Pago) refers
           to the method used to settle the invoice, such as cash, credit card, bank transfer, etc.
        """,
    'depends': ['payment', 'website_sale', 'l10n_mx_edi_sale'],
    'data': [
        'data/mail_data.xml',
        'views/payment_provider_view.xml',

    ],
    'installable': True,
    'auto_install': False,
}
