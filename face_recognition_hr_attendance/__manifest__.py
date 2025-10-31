# -*- coding: utf-8 -*-
{
    "name": "HR Attendance Face Recognition",
    "summary": "Employee Attendance using Face Recognition",
    "description": """
        This module converts normal attendance to facial recognition attendance.
        Configure employee images; those images will be used for face recognition.
        HR Attendance
    """,
    "author": "ErpMstar Solutions",
    "category": "Human Resources/Attendances",
    "version": "1.0",
    "depends": ["hr_attendance", "web_widget_image_cam"],

    "data": [
        "security/ir.model.access.csv",
        "security/attendance_security.xml",
        "views/views.xml",
        "views/templates.xml",
        "views/res_config_settings_views.xml",
    ],

    "demo": [],

    "assets": {
        # Este bundle es el que usa el Kiosk público de Asistencias
        "hr_attendance.assets_public_attendance": [
            # (opcional) jQuery/Bootstrap si realmente los necesitas
            "web/static/lib/jquery/jquery.js",
            "web/static/lib/popper/popper.js",
            "web/static/lib/bootstrap/js/dist/util/index.js",
            "web/static/lib/bootstrap/js/dist/dom/data.js",
            "web/static/lib/bootstrap/js/dist/dom/event-handler.js",
            "web/static/lib/bootstrap/js/dist/dom/manipulator.js",
            "web/static/lib/bootstrap/js/dist/dom/selector-engine.js",
            "web/static/lib/bootstrap/js/dist/util/config.js",
            "web/static/lib/bootstrap/js/dist/util/component-functions.js",
            "web/static/lib/bootstrap/js/dist/util/backdrop.js",
            "web/static/lib/bootstrap/js/dist/util/focustrap.js",
            "web/static/lib/bootstrap/js/dist/util/sanitizer.js",
            "web/static/lib/bootstrap/js/dist/util/scrollbar.js",
            "web/static/lib/bootstrap/js/dist/util/swipe.js",
            "web/static/lib/bootstrap/js/dist/util/template-factory.js",
            "web/static/lib/bootstrap/js/dist/base-component.js",
            "web/static/lib/bootstrap/js/dist/alert.js",
            "web/static/lib/bootstrap/js/dist/button.js",
            "web/static/lib/bootstrap/js/dist/carousel.js",
            "web/static/lib/bootstrap/js/dist/collapse.js",
            "web/static/lib/bootstrap/js/dist/dropdown.js",
            "web/static/lib/bootstrap/js/dist/modal.js",
            "web/static/lib/bootstrap/js/dist/offcanvas.js",
            "web/static/lib/bootstrap/js/dist/tooltip.js",
            "web/static/lib/bootstrap/js/dist/popover.js",
            "web/static/lib/bootstrap/js/dist/scrollspy.js",
            "web/static/lib/bootstrap/js/dist/tab.js",
            "web/static/lib/bootstrap/js/dist/toast.js",
            "web/static/src/libs/bootstrap.js",

            # 👇 MUY IMPORTANTE: primero face-api, DESPUÉS tu implementación
            #"face_recognition_hr_attendance/static/src/js/face-api.min.js",
            "face_recognition_hr_attendance/static/src/js/face_attendance_py_implementation.js",

            # Templates si los usas
            "face_recognition_hr_attendance/static/src/xml/*.xml",
        ],

        # CSS opcional para el sitio (NO metas face-api aquí)
        "web.assets_frontend": [
            "face_recognition_hr_attendance/static/src/css/kiosk.css",
        ],
    },

    "installable": True,
    "auto_install": False,
    "application": True,
    "external_dependencies": {
        "python": ["cmake", "dlib", "face_recognition", "numpy", "opencv-python"],
    },
    "images": ["static/description/banner.jpg"],
}