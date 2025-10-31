# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Core Violation Report',
    'version': '18.0.0.0',
    'category': 'Human Resources/Attendances',
    'summary': 'Track employee attendance',
    'description': """
                This module aims to manage employee's violation of check-in and check-out.
       """,
    'license': "LGPL-3",
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'depends': ['hr_attendance'],
    'data': ['security/ir.model.access.csv',
             'wizard/core_violation.xml',
             'report/core_violation_report.xml',
             'report/core_violation_template.xml'
             ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
