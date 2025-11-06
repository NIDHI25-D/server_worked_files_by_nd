{
    'name': 'Setu Credit Bureau',
    'version': '18.0.0.0',
    'category': '',
    'license': 'LGPL-3',
    'description': """it creates a report of credit bureau for the contacts.""",
    'summary': 'Setu Credit Bureau',

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'maintainer': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com/',
    'support': 'support@setuconsulting.com',

    # Dependencies
    'depends': ['web', 'base_vat', 'sale_marvelsa', 'setu_accounts_report_extended', 'setu_ecommerce_checkout_extended'],

    # Views
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'wizard/credit_bureau_report_wiz_view.xml',

    ],

    'assets': {
        'web.assets_backend': [
            'setu_credit_bureau/static/src/css/custom_css.css',
            'setu_credit_bureau/static/src/components/*/*.js',
            'setu_credit_bureau/static/src/components/*/*.xml'
        ],
    },

    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
}