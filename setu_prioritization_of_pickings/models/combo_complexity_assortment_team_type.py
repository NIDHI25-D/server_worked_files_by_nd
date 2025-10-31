from odoo import fields, models, api


class ComplexityAssortmentTeamTypes(models.Model):
    _name = 'combo.complexity.assortment.team.type'

    combo_assortment_team_type_id = fields.Many2one(comodel_name='assortment.team.types', string='Team',ondelete='cascade')
    stock_picking_ids = fields.Many2many('stock.picking', 'stock_picking_combo_assortment_team_type_rel',
                                         string='Pending Transfers')
    complexity_levels_id = fields.Many2one('complexity.levels',string='Complexity Level')