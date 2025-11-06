{
    'name': 'Setu Customer Ratings',
    'version': '18.0.0.0',
    'description': 'This module contains functionality to get scores of customers based on their sales history and '
                   'accounting history.',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'license': 'LGPL-3',
    'depends': ['sale', 'point_of_sale', 'setu_rfm_analysis', 'l10n_mx_edi','queue_job'],
    'data': ['security/res_groups_views.xml',
             'security/ir.model.access.csv',
             'views/score_conf_views.xml',
             'views/customer_rating_views.xml',
             'views/customer_score_views.xml',
             'data/customer_rating_data.xml',
             'data/score_conf_data.xml',
             'data/score_conf_line_price_data.xml',
             'data/score_conf_line_percentage_data.xml',
             'data/score_conf_line_qty_data.xml',
             'data/cron_get_customer_scores_data.xml',
             'data/queue_job_data.xml',
             'views/res_partner_views.xml',
             'views/setu_partner_rating_history_views.xml',
             # 'reports/setu_history_management_report.xml',
             'wizard/res_config_settings_views.xml',
             'wizard/score_conf_creator_views.xml',
             'views/menu_items_views.xml',
             'db_function/get_currency_rate.sql',
             'db_function/create_customer_score_records.sql',
             'db_function/set_customer_scores.sql',
             'db_function/set_document_ids.sql',
             'db_function/update_rating_data.sql'
             ],
    'qweb': ['static/src/xml/dashboard.xml'],
    'assets': {
        'web.assets_backend': [
            'setu_customer_rating/static/src/css/color_for_field_lable.css',
        ],

    },

    'demo': [],
    'installable': True,
    'auto_install': False
}
