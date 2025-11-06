# -*- coding: utf-8 -*-
###################################################################################
#   A part of OpenHRMS Project <https://www.openhrms.com>
#
#   Author : Setu Consulting Services Pvt. Ltd.
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.
#
###################################################################################
{
    'name': 'Open HRMS Overtime',
    'version': '18.0.0.0',
    'summary': 'Manage Employee Overtime',
    'description': """
        Helps you to manage Employee Overtime.
        """,
    'category': 'eCommerce',
    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com/",
    'depends': [
        'hr_attendance', 'project','om_hr_payroll'
    ],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'data': [
        # 'views/assets.xml',
        'data/data.xml',
        'security/security.xml',
        'views/overtime_request_view.xml',
        'views/overtime_type.xml',
        'views/hr_contract.xml',
        # 'views/hr_payslip.xml',
        'views/hr_employee.xml',
        'security/ir.model.access.csv',
    ],
    # 'qweb': [
    #     'static/src/xml/activity.xml',
    # ],
    'demo': ['data/hr_overtime_demo.xml'],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
