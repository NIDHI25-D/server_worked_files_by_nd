# -*- encoding: utf-8 -*-
{
    'name': 'Account Assets',
    'summary': 'Print responsive letter for employee',
    'category': 'Partner',
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'depends': ['sale_management', 'account_asset', 'hr', 'l10n_mx_edi_extended'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_asset.xml',
        'views/hr_employee_views.xml',
        'report/responsive_letter_report.xml',
        'report/responsive_letter_template.xml',
    ],
    'installable': True,
}
