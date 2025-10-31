# -*- coding: utf-8 -*-
{
    'name': "Setu Prioritization Of Pickings",

    'summary': """  
        To prioritize the pickings in a single line for each warehouse based on
        priority levels, line complexity and importance levels. This module form a
        consecutive for assigning pickings to the assortment teams automatically.
        """,

    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': "https://www.setuconsulting.com",
    'license': 'LGPL-3',
    'category': 'Transfers',
    'version': '18.0.0.0',

    'depends': ['marvelfields','setu_urgent_order_enhancement'],

    'data': [
        'security/ir.model.access.csv',
        'views/crm_team.xml',
        'views/complexity_levels.xml',
        'views/assortment_team.xml',
        'views/assortment_team_types.xml',
        'views/priority_rules.xml',
        'views/stock_picking.xml',
        'views/combo_complexity_assortment_tem_type.xml',
        'data/prioritization_cron.xml',
    ],
}
