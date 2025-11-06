# -*- encoding: utf-8 -*-
# See README.rst file on addons root folder for license details
{
    "name": "No Negative Stock",
    "summary": "Negative stocks are not allowed",
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    "category": "Generic Modules/Stock",
    "depends": ["stock"],
    "data": [
        "views/res_config_view.xml",
        "views/stock_location_view.xml"
    ],
    "images": ["static/description/main_screenshot.png"],
    "installable": True,
    "development_status": "Mature",
}
