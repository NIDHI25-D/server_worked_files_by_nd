from . import models
from . import reports
from odoo.tools import convert_file

def pre_init(cr):
    convert_file(cr, 'stock_cycle_count', 'data/ir.model.csv', None, mode='init')
    convert_file(cr, 'stock_cycle_count', 'data/ir.model.fields.csv', None, mode='init')
