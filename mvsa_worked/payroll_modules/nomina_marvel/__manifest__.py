# -*- coding: utf-8 -*-

{
    'name': 'Nomina Marvel',
    'summary': 'Agrega modificaciones para la nómina de Marvel.',
    'description': '''
            Nomina Marvel
    ''',
    'author': 'IT Admin',
    'version': '16.03',
    'category': 'Employees',
    'depends': [
        'nomina_cfdi_ee',
    ],
    'data': [
        'views/hr_contract_view.xml',
        'views/hr_payroll_payslip_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}
