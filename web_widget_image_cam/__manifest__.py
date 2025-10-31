# -*- coding: utf-8 -*-

{
    'name': 'Image WebCam Widget',
    'version': '1.0',
    'category': 'Tool',
    'sequence': 6,
    'author': 'ErpMstar Solutions',
    'summary': "Allow you to capture image from your webcam in image widget.",
    'description': "Allow you to capture image from your webcam in image widget.",
    'depends': ['web'],
    'data': [
        # 'views/views.xml',
        'view/web.xml',
    ],

    'assets': {
        'web.assets_backend': [
            '/web_widget_image_cam/static/src/js/widget.js',
            '/web_widget_image_cam/static/src/js/face-api.min.js',
            '/web_widget_image_cam/static/src/js/webcam.js',
            '/web_widget_image_cam/static/src/css/widget.css',
            '/web_widget_image_cam/static/src/xml/widget.xml',
            # 'web/static/src/legacy/js/core/**.js',
            #
            # 'web/static/src/legacy/xml/dialog.xml',
        ],

    },

    'images': [
        'static/description/banner.jpg',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'price': 10,
    'currency': 'EUR',
}
