# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Artem Shurshilov <shurshilov.a@yandex.ru>
# License OPL-1.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "hr attendance face recognition pro",

    'summary': """
Face recognition check in / out
is a technology capable of identifying or verifying a person
from a digital image or a video frame from a video source""",

    'author': "EURO ODOO, Shurshilov Artem",
    'website': "https://eurodoo.com",
    # "live_test_url": "https://eurodoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '18.0',
    "license": "OPL-1",
    'price': 122,
    'currency': 'EUR',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],



    "cloc_exclude": [
        "static/src/js/lib/**/*",  # exclude a single folder
    ]
}
