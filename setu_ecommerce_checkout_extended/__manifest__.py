# -*- coding: utf-8 -*-
{
    "name": "Setu Ecommerce Checkout Extended",
    "category": "Website",
    "version": "18.0.0.0",
    "author": "Setu Consulting Services Pvt. Ltd.",
    'license': "LGPL-3",
    "website": "https://www.setuconsulting.com",
    "description": """Setu Ecommerce Checkout Extended""",
    # "depends": ['website_sale', 'setu_cfdi_and_payment_way', 'marvelsa_sepomex','l10n_mx_edi_extended','partner_category_hierarchy'],
    "depends": ['website_sale', 'l10n_mx_edi_extended', 'partner_category_hierarchy', 'marvelsa_sepomex'],
    "data": [
        'views/res_partner.xml',
        'views/manage_address_view.xml',
        'views/website.xml',
        'views/auth_signup_login_templates.xml',
        'data/res_partner_data.xml',
        'data/email_template.xml',
        'views/res_config_setting.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            "setu_ecommerce_checkout_extended/static/src/scss/main.scss",
            "setu_ecommerce_checkout_extended/static/src/js/main.js",
            "setu_ecommerce_checkout_extended/static/src/js/manage_contact.js"
        ]
    },
    "demo": [],
}
