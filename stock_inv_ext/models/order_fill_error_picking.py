from odoo import models, fields, api, _

class OrderFillErrorPicking(models.Model):
    _name = 'order.fill.error.picking'

    name = fields.Char(string="Transfer Cancellation Reason")