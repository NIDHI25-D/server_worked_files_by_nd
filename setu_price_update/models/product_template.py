from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    competition_level_id = fields.Many2one('competition.level', string="Competition Level", ondelete="restrict")
    import_factor_level_id = fields.Many2one('import.factor.level', string="Import Level Factor", ondelete="restrict")

