from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_created_from_instalment = fields.Boolean()
