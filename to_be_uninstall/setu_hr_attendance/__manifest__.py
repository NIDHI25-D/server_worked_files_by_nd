# -*- coding: utf-8 -*-
# Copyright (C) 2019 Artem Shurshilov <shurshilov.a@yandex.ru>
# License OPL-1.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Setu Offline Attendance Module with kiosk",

    'summary': """
    
    """,

    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://setuconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '18.0.0.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'hr_attendance','hr_attendance_geo_html'],

    # always loaded
    'data': [
        'views/res_company_views.xml',
        # 'views/views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'setu_hr_attendance/static/src/js/kiosk_mode_face_recognition.js',
            'setu_hr_attendance/static/src/js/my_attendance_face_recoginition.js',
            # 'setu_hr_attendance/static/src/js/geo_attendance.js',
            'setu_hr_attendance/static/src/xml/base.xml',
        ],
    }
}
