# -*- coding: utf-8 -*-
# Part of Odoo. ee LICENSE file for full copyright and licensing details.
{
    'name': 'Setu Recruitment Enhancement',
    'category': 'HR/Recruitment',
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'depends': ['hr_recruitment','website_hr_recruitment' ],
    'data': [ 'security/recruitment_security.xml',
        'views/recruitment_enhancement.xml'
    ],
    'installable': True,
}
