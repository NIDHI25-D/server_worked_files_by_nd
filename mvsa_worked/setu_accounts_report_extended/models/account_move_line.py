from odoo import models, fields, api, _
from odoo.tools.sql import SQL
import re
import itertools

regex_field_agg = re.compile(r'(\w+)(?::(\w+)(?:\((\w+)\))?)?')  # For read_group


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # to add group operator
    amount_currency = fields.Monetary(aggregator='sum')
    blocked = fields.Boolean(
        string='No Follow-up',
        default=False,
        help="You can check this box to mark this journal item as a litigation with the "
             "associated partner",
    )