from odoo import fields, models


class OperativeSystemVersion(models.Model):
    _name = 'operative.system.version'
    _description = 'Operative System Version'

    name = fields.Char()
    operative_system_distribution_id = fields.Many2one('operative.system.distribution',
                                                       string='Operative System Distribution')
