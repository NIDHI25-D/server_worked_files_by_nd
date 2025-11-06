# -*- coding: utf-8 -*-
{
    # App Information
    'name': 'Log Note',
    'category': 'Productivity',
    'version': '18.0.0.0',
    "sequence": 1,
    'license': 'OPL-1',
    "summary": """Log Note Module helps you to manage the different Model with fields log added in the chatter""",
    "description": """Log Note Module helps you to manage the different Model with fields log added in the chatter""",

    # Author
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'maintainer': 'Setu Consulting Services Private Limited',
    'website': 'https://www.setuconsulting.com/',

    # Dependencies
    'depends': ['mail'],

    # Views
    'data': [
        "views/ir_model_views.xml"],

    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,
}
