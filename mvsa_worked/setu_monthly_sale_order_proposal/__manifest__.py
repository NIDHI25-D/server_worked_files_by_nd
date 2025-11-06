# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Setu Create Monthly Sale Order Proposal',
    'version': '18.0',
    'category': 'sale',
    'summary': """create monthly sale order proposal for every customer""",
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """

    """,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'license': 'OPL-1',
    'sequence': 25,
    'depends': ['website_sale_stock','queue_job','partner_category_hierarchy','setu_customer_lock'
        ,'setu_website_preorder'],

    'data': [
        'security/ir.model.access.csv',
        'data/create_monthly_sale_order_proposal.xml',
        'views/res_config_settings_view.xml',
        'views/template.xml',
        'views/res_partner.xml',
        'views/update_so_price_view.xml',
        'data/mail_template.xml',
        'data/update_so_price_per_product.xml',
        'data/que_job_demo_data.xml'
    ],
    'application': True,
}
