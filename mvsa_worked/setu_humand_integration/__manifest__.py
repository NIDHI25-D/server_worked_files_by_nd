{
    "name": "Setu API Humand Integration",
    'version': '18.0.0.0',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'license': 'LGPL-3',
    'depends': ['base','hr','hr_recruitment','hr_holidays','nomina_cfdi_ee'],
    'data': [
        'data/setu_create_time_off_requests_from_humand_cron.xml',
        'views/res_company_views.xml',
        'views/hr_leave_type.xml',
        'views/hr_leave_views.xml',
        'views/res_config_settings_views.xml',
        'views/hr_employee_views.xml',
    ],
    'application': False,
    'assets': {}
}