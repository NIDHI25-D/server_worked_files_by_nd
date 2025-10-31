# -*- encoding: utf-8 -*-
{
    'name': 'Setu POS Return Order Enhancement',
    'description': """Setu POS Return Order Enhancement""",
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'version': '18.0.0.0',
    'license': 'LGPL-3',
    'category': 'Point Of Sale',
    'summary': """It is used to break create returnd of refund the order and manage it's quantity""",
    'website': 'https://www.setuconsulting.com',
    'depends': ['point_of_sale', 'sale'],
    'data': [
        'views/pos_payment_inherit.xml',
    ],
    'application': False,
}
