# -*- coding: utf-8 -*-
{
    'name': 'Partners Hierarchy',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'description': """Partners Hierarchy""",
    'category': 'Website',
    'license': 'LGPL-3',
    'version': '18.0.0.0',
    'website': 'https://setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'currency': 'EUR',
    'summary': 'Build partners hierarchy by specifying partner categories',
    'data': ['security/res_groups.xml',
             'security/ir.model.access.csv',
             'data/product_pricelist.xml',
             'views/res_partner.xml',
             'views/res_partner_hcategory.xml',
             'views/sale_order.xml'
             ],
    'depends': ['website_sale'],
    # 'assets': {
    #     'web.assets_common': [
    #         'partner_category_hierarchy/static/src/js/tour.js'
    #     ],
    # },
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'price': 10.0,
}
