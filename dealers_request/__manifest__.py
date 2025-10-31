# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Dealers Request',
    'version': '18.0.0.0',
    'license': "LGPL-3",
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'depends': ['documents', 'setu_ecommerce_checkout_extended'],
    'data': [
        'data/documents_document_data.xml',
        'data/documents_tag_data.xml',
        'data/ir_actions_server_data.xml',
        'data/dealer_request_sequence.xml',
        'data/mail_templates.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/dealers_request.xml',
        'views/res_partner.xml',
        'views/documents_document.xml',
        'views/documents_document_views.xml',
        'views/credit_limit_requested.xml',
        'views/credit_days_requested.xml',
        'views/reject_reason.xml',
        'views/website.xml',
        'views/res_company.xml',

    ],
    'assets': {
        'web.assets_frontend': [
            "dealers_request/static/src/scss/main.scss",
            "dealers_request/static/src/js/main.js",
        ],
         'web.assets_backend': [
             "dealers_request/static/src/components/documents_details_panel/documents_details_panel.xml",
         ]
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
}
