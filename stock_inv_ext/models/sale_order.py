from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_studio_comentarios = fields.Text(string='Comentarios')







