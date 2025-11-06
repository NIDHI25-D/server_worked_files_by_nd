# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Views For Data Studio',
    'version': '16.0',
    'category': 'product',
    'summary': """
    """,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'license': "LGPL-3",
    'description': """ Product View By Vendor
    """,
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'depends': ['mass_mailing','queue_job','sale','purchase','account','product','crm'],
    'data': [
        'security/ir.model.access.csv',
        'security/email_group.xml',
        'data/refresh_materialized_view.xml',
        'views/res_config_setting.xml',
        'data/job_function_channel_demo_data.xml'
     ],
    "pre_init_hook": "pre_init_input_query"
}
