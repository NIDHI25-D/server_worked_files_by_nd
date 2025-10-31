# -*- coding: utf-8 -*-
{
    'name': "setu_ecommerce_modification",
    'summary': """
        Modification in website address page""",
    'author': "Setu Consulting Services Pvt. Ltd.",
    'license': "LGPL-3",
    'website': "https://www.setuconsulting.com",
    'category': 'Website',
    'version': '18.0.0.0',
    'depends': ['website_sale', 'auth_oauth'],
    'data': [
        'data/email_template.xml',
        'data/ir_cron.xml',
        'views/templates.xml',
        'views/auth_signup_login_templates.xml',
        # 'views/sale_order.xml', have to review can't see the purpose of declared field
    ],
}
