# -*- encoding: utf-8 -*-
# Copyright 2022 Shurshilov Artem<shurshilov.a@yandex.ru>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Web Widget - Image WebCam",
    "summary": """Allows to take image with WebCam
    [TAGS] web camera web foto web photo web images camera 
    image snapshot web snapshot webcam snapshot picture web contact
    image web product image online mobile web image produt mobile""",
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com",
    "category": "web",
    "price": 19.00,
    "images": [
        "static/description/field.png",
        "static/description/choose.png",
    ],
    "currency": "EUR",
    "depends": [
        "web",
    ],
    "assets": {
        'web.assets_backend': [
            'web_image_webcam/static/src/js/image_field.js',
            'web_image_webcam/static/src/js/webcam_dialog.js',
            'web_image_webcam/static/src/xml/web_widget_image_webcam.xml',
            'web/static/lib/jquery/jquery.js',
        ],
    },
    "installable": True,
}
