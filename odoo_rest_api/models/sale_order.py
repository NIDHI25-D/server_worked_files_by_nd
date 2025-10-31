from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    api_create_sale_order = fields.Boolean(string="Is Sale Order From Api?", default=False)

