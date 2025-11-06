# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Setu Advance Budget Management',
    'version': '18.0.0.0',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',

    # Dependencies
    'depends': [ "base","web","mail","account"],

    # Views
    'data': ['security/ir.model.access.csv',
             'views/setu_advance_budget_forecasted_recreation_views.xml',
             'views/setu_advance_budget_forecasted_views.xml',
             'views/setu_advance_budget_forecasted_sheet_views.xml',
             'views/setu_advance_budget_forecasted_sheet_line_views.xml',
             'views/setu_advance_budget_forecasted_position_views.xml',
             'report/search_template_views.xml',
             'wizard/setu_export_data.xml',
             'views/account_report.xml',
             'views/res_config_settings.xml'],

    'assets': {
        'web.assets_backend': [
            '/setu_advance_budget_management/static/src/js/account_reports.js',
            'setu_advance_budget_management/static/src/scss/account_report.css'
        ],

    },

    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,
}
