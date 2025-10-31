# -*- coding: utf-8 -*-
#################################################################################
# Author      : CodersFort (<https://codersfort.com/>)
# Copyright(c): 2017-Present CodersFort.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://codersfort.com/>
#################################################################################
{
    "name": "Employee Performance (NineBox Employee Performance)",
    "summary": "NineBox Employee Performance",
    "version": "18.0.0",
    "description": """NineBox Employee Performance""",
    "version": "1.0.0",
    "author": "Setu Consulting Services Pvt. Ltd.",
    "license": "Other proprietary",
    "website": "https://www.setuconsulting.com",
    "images": ["images/employee_performance.png"],
    "category": "HR",
    "depends": [
        "base",
        "hr",
        "web"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/assessment_rating_data.xml",
        "report/ninebox_report_qweb.xml",
        "report/ninebox_report_qweb_template.xml",
        # "views/assets.xml",
        "views/ninebox_report.xml",
        "views/review_schedule.xml",
        "views/review_period_timeline.xml",
        "views/employee_performance_view.xml",
        "views/assessment_rating.xml",
        "views/hr_views.xml",
        "views/employee_assessment_questions_view.xml",
        "views/manager_assessment_questions_view.xml",

    ],
    "qweb": [
        "static/src/xml/control_buttons.xml",
        "static/src/xml/ninebox_report_view.xml",
    ],
    'assets': {
        'web._assets_primary_variables': [
        ],
        'web.assets_backend': [
            'ninebox_employee_performance/static/src/css/style.css',
            'ninebox_employee_performance/static/src/js/ninebox_report.js',
            'ninebox_employee_performance/static/src/xml/**/*'
        ],
        'web.assets_frontend': [
        ],
        'web.assets_tests': [
        ],
        'web.qunit_suite_tests': [
        ],
        'web.report_assets_common': [
            'ninebox_employee_performance/static/src/css/report_style.css',
        ],
    },
    "installable": True,
    "application": True,
    "price": 80,
    "currency": "EUR",
    "pre_init_hook": "pre_init_check",
}
