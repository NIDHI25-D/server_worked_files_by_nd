# -*- coding: utf-8 -*-
{
    "name": "Setu Customer Statistics On Portal",
    "version": "18.0.0.0",
    "author": "Setu Consulting Services Pvt. Ltd.",
    'license': "LGPL-3",
    "website": "https://www.setuconsulting.com",
    "depends": ['portal','account','setu_sales_time_dashboard','setu_accounts_report_extended'],
    'data': [
        "views/my_statistics.xml",
        "views/portal_charts.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'setu_customer_statistics_on_portal/static/src/js/portal_data.js',
        ],
    },
}
