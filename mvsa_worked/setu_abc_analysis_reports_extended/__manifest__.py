# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'ABC Sales Analysis Reports Extended',
    'version': '18.0.0.0',
    'price': 179,
    'currency': 'EUR',
    'category': 'sale',
    'summary': """ABC Sales Analysis Reports, 
                  Inventory XYZ Analysis Report, 
                  ABC-XYZ Combine Analysis Report, 
                  ABC Sales Frequency Analysis Report""",
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """
        Extended Part of ABC Sales Analysis Reports
    """,
    'author': 'Setu Consulting',
    'license': 'OPL-1',
    'sequence': 25,
    'depends': ['setu_abc_analysis_reports','web'],
    'data': [
        'data/cron_jobs.xml',
        'views/res_config_settings.xml',
        'views/product_product.xml',
        'db_function/get_abc_sales_analysis_data_company_wise.sql',
    ],
    'application': True,
    # 'pre_init_hook': 'pre_init',
}
