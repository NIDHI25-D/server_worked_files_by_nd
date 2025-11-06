# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Advanced Inventory Reports',
    'version': '18.0.0.3',
    'price': 299,
    'currency': 'EUR',
    'category': 'stock',
    'summary': """	
        advance inventory ieports / Inventory Analysis Reports
        inventory Turnover Analysis Report / Inventory Turnover Ratio / turnover report / warehouse turnover
        inventory FSN Analysis Report / non moving report / warehouse analysis
        inventory XYZ Analysis Report / turn over report / warehouse turn over
        inventory FSN with XYZ Analysis Report / FSN-XYZ Analysis / FSN XYZ Analysis
        inventory age report / stock ageing / Inventory ageing / stock age / inventory aging / ageing report
        inventory age breakdown report
        inventory overstock report / excess inventory report  
        stock movement report / stock rotation report 
        inventory Out Of Stock Report / inventory coverage report / outofstock report
        Advanced Inventory Reports / All in one inventory reports / all in one reports
        Inventory Management, Advanced reports, Advance report, inventory management technique, inventory coverage ratio,
        sales analysis, sales report, sales analytics, analytic reports, analytical reports, accurate inventory,
		""",
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """
        Advance Inventory Reports / Inventory Analysis Reports
        ===================================================================
        - Inventory Turnover Analysis Report
            Inventory turnover is a ratio showing how many times a company has sold and replaced inventory during a given period.
    
        - Inventory FSN Analysis Report
            This classification is based on the consumption pattern of the products i.e. movement analysis forms the basis. 
            Here the items are classified into fast moving, slow moving and non-moving on the basis of frequency of transaction. 
    
        - Inventory XYZ Analysis Report
            XYZ Analysis is always done for the current Stock in Inventory and aims at classifying the items into three classes on the basis of their Inventory values.
            
        - Inventory FSN with XYZ Analysis Report
            FSN Classification analysis along with XYZ Classification
            
        - Inventory Age Report
            Inventory age report is useful to determine how oldest your inventories are.
            It gives you detailed analysis products wise about oldest inventories at company level.
        
        - Inventory Age Breakdown Report
            Inventory age breakdown report is useful to determine how oldest your inventories are.
            It gives you detailed breakdown analysis products wise about oldest inventories at company level.
            
        - Inventory Overtsock Report / Excess Inventory Report  
            Excess Inventory Report is used to capture all products which are having overstock than needed.
        
        - Stock Movement Report / Stock Rotation Report
            Stock movement report is used to capture all the transactions of products between specific time frame.   
   
        - Inventory Out Of Stock Report
            Inventory OutOfStock Report is used to capture all products which are having demand but stock shortage as well.
    """,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'license': 'OPL-1',
    'sequence': 25,
    'depends': ['sale_stock', 'purchase_stock'],
    'images': ['static/description/banner.gif'],
    'data': [
        'security/ir.model.access.csv',
        'views/setu_inventory_dashboard_menu.xml',
        'views/setu_stock_movement_report.xml',
        'views/res_company.xml',
        'views/setu_inventory_turnover_analysis_report.xml',
        'views/setu_inventory_fsn_analysis_report.xml',
        'views/setu_inventory_fsn_company_wise_report.xml',
        'views/setu_inventory_xyz_analysis_report.xml',
        'views/setu_inventory_fsn_xyz_analysis_report.xml',
        'views/setu_inventory_overstock_report.xml',
        'views/setu_inventory_outofstock_report.xml',
        'views/setu_inventory_age_report.xml',
        'views/setu_inventory_age_breakdown_report.xml',
        'db_function/get_category_company_dependent.sql',
        'db_function/get_product_company_dependent.sql',
        'db_function/get_stock_data.sql',
        'db_function/get_sales_transaction_data.sql',
        'db_function/get_products_forecasted_stock_data.sql',
        'db_function/get_products_overstock_data.sql',
        'db_function/get_products_stock_movements.sql',
        'db_function/get_products_opening_stock.sql',
        'db_function/get_inventory_turnover_ratio_data.sql',
        'db_function/get_inventory_turnover_ratio_data_company_vise.sql',
        'db_function/get_inventory_fsn_analysis_report.sql',
        'db_function/get_inventory_fsn_analysis_report_company_vise.sql',
        'db_function/get_inventory_xyz_analysis_data.sql',
        'db_function/get_inventory_fsn_xyz_analysis_report.sql',
        'db_function/get_products_outofstock_data.sql',
        'db_function/inventory_stock_age_report.sql',
        'db_function/get_inventory_age_breakdown_data.sql',
    ],
    'assets': {
        'web.assets_backend': [
            'setu_advance_inventory_reports/static/src/xml/panel_content.xml',
            'setu_advance_inventory_reports/static/src/js/fsn_dashboard.js',
            'setu_advance_inventory_reports/static/src/js/overstock_dashboard.js',
            'setu_advance_inventory_reports/static/src/js/outofstock_dashboard.js',
            'setu_advance_inventory_reports/static/src/js/fsn_xyz_dashboard.js',
            'setu_advance_inventory_reports/static/src/js/xyz_dashboard.js',
            'setu_advance_inventory_reports/static/src/js/movement_analysis_dashboard.js',
            'setu_advance_inventory_reports/static/src/js/age_breakdown_dashboard.js',
            'setu_advance_inventory_reports/static/src/xml/fsn_dashboard_content.xml',
            'setu_advance_inventory_reports/static/src/xml/fsn_xyz_content.xml',
            'setu_advance_inventory_reports/static/src/xml/overstock_dashboard_content.xml',
            'setu_advance_inventory_reports/static/src/xml/outofstock_dashboard.xml',
            'setu_advance_inventory_reports/static/src/xml/xyz_dashboard_content.xml',
            'setu_advance_inventory_reports/static/src/xml/movement_analysis_content.xml',
            'setu_advance_inventory_reports/static/src/xml/age_breakdown_content.xml',
            'setu_advance_inventory_reports/static/src/scss/fsn.scss',
            'setu_advance_inventory_reports/static/src/scss/box.scss',
        ],
    },
    'application': True,
    'live_test_url': 'https://www.youtube.com/playlist?list=PLH6xCEY0yCICqQFq_m64Boo-11RkLVIfM',
}
