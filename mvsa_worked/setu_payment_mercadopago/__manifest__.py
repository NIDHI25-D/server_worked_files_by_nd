# -*- coding: utf-8 -*-

{
    'name': 'MercadoPago Payment Acquirer',
    'category': 'Accounting/Payment Acquirers',
    'sequence': 365,
    'version': '18.0.0.1',
    'license': "LGPL-3",
    'description': """MercadoPago Payment Acquirer""",
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'depends': ['payment_mercado_pago', 'setu_payment_acqirers'],

    'data': [
        'views/mercadopago.xml',
        'views/payment_acquirer.xml',
        'data/payment_provider_views.xml',
        'data/auto_payment_transaction_state_update_cron.xml',
    ],
    'images': ['src/img/mercadopago_icon.png', 'src/img/mercadopago_logo.png',
               'src/img/mercadopago_logo_64.png'],
    'assets': {
        'web.assets_frontend': [
            'setu_payment_mercadopago/static/src/js/payment_form.js',
        ],
    },
    'installable': True,
    'application': False,
}
