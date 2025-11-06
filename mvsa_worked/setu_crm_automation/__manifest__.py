# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    # App information
    'name': 'Setu Crm Automation',
    'version': '18.0.0.0',
    'category': 'Lead/Opportunity',
    # 'license': 'OPL-1',
    'license': 'LGPL-3',
    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """Update product price based on Range and different level""",

    # Dependencies
    'depends': ['sale_crm', 'setu_sales_time_dashboard'],

    # View
    'data': [
              'data/crm_sequence.xml',
              'security/crm_security_groups.xml',
              'data/new_stage.xml',
              'views/crm_setting_view.xml',
              'data/change_state_of_opportunity.xml',
              'views/crm.xml',
              'views/sale_order.xml'

    ],

    # Technical
    'installable': True,
    # 'auto_install': False,
    # 'application': False,
    # 'active': False,

}

