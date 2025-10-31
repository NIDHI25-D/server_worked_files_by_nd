from odoo import models, fields, api


class SaleReport(models.Model):
    _inherit = 'account.move'

    rutav = fields.Char(string='Ruta', related='partner_id.rutav', store=True)
    zone_id = fields.Many2one('res.partner.zone', string="Zone", related='partner_id.zone_id', store=True)

