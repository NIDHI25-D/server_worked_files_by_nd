{
    'name': 'Web Forecast Dashboard Custom',
    'version': '17.0.1.0.0',
    'category': 'Forecast',
    'summary': 'Customizations for Forecast Export Wizard',
    'description': """
        This module extends `web_forecast_dashboard` and allows adding custom fields and logic for list view.
    """,
    'author': 'Setu Consulting Services Pvt.Ltd',
    'license': 'LGPL-3',
    'depends': ['web_forecast_dashboard'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_product.xml',
        'views/forecast_report_history.xml',
        'views/forecast_report_line.xml',
        'views/forecast_trigger_main.xml',
        'views/purchase_order.xml',
        'views/forecast_report_amz_margin.xml',
        'wizard/ext_forecast_export_wizard_view.xml',
        'wizard/forecast_report_import_amz_margin_file.xml',
        'wizard/forecate_create_po_wizard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'setu_web_forecast_dashboard/static/src/js/forecast_list_color.js',
            'setu_web_forecast_dashboard/static/src/css/forecast_tree.css',

            'setu_web_forecast_dashboard/static/src/js/list_view_sticky_header_and_column.js',
            'setu_web_forecast_dashboard/static/src/xml/list_view_sticky_header_and_column.xml',
            'setu_web_forecast_dashboard/static/src/scss/list_view_sticky_header_and_column.scss',
        ],

    },

    'installable': True,
    'application': False,
}
