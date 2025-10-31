from odoo import fields, models


class OperativeSystemDistribution(models.Model):
    _name = 'operative.system.distribution'
    _description = 'Operative System Distribution'

    name = fields.Char()
    operative_system_type_id = fields.Many2one('operative.system.type', string='Operative System Type')
