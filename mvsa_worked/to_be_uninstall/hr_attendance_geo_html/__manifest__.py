{
    "name": "Hr Attendance Professional Policy Geolocation HTML",
    "summary": "This module helps to enhance HR Attendance",
    "category": "Human Resources",
    "version": "18.0.0.0",
    "license": "LGPL-3",
    "author": "Setu Consulting Services Pvt. Ltd.",
    "website": "https://www.setuconsulting.com",
    "depends": ["hr_attendance_base"],
    "data": [
        "views/hr_attendance_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_attendance_geo_html/static/src/**/*.js",
        ],
    }   
}