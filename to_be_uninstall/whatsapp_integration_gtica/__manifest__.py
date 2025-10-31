# -*- coding: utf-8 -*-
{
    'name': 'Whatsapp Integration All in One',
    'summary': 'Integration Whatsapp for Sale, CRM, Invoice, Delivery and more',
    'version': '18.0.0.0',
    'category': 'Administration',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'support': 'support@setuconsulting.com',
    'website': 'https://www.setuconsulting.com',
    'license': 'OPL-1',
    'price': 41.99,
    'currency': 'EUR',
    'depends': ['base', 'crm', 'sale_management', 'sales_team', 'purchase', 'account', 'stock'],
    'assets': {
        'web.assets_backend': [
            'whatsapp_integration_gtica/static/src/js/whatsapp_script.js'
        ],
    },
    'data': [
        'data/data_whatsapp_default.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/view_whatsapp_integration_template.xml',
        'views/view_integration_crm.xml',
        'views/view_integration_sale.xml',
        'views/view_integration_purchase.xml',
        'views/view_integration_invoice.xml',
        'views/view_integration_payment.xml',
        'views/view_integration_partner.xml',
        'views/view_integration_stock_picking.xml',
        'wizard/wizard_whatsapp_integration_crm.xml',
        'wizard/wizard_whatsapp_integration_sale.xml',
        'wizard/wizard_whatsapp_integration_purchase.xml',
        'wizard/wizard_whatsapp_integration_invoice.xml',
        'wizard/wizard_whatsapp_integration_payment.xml',
        'wizard/wizard_whatsapp_integration_partner.xml',
        'wizard/wizard_whatsapp_integration_delivery.xml',
        'templates/templates.xml'
    ],
    'qweb': [
        'static/src/xml/website_facebook_chat_live.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'application': True,
    'installable': True,
}
