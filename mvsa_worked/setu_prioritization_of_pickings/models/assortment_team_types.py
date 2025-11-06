from odoo import fields, models, api,_
from odoo.exceptions import ValidationError


class AssortmentTeamTypes(models.Model):
    _name = 'assortment.team.types'

    name = fields.Char(string='Name')
    operation_types_ids = fields.Many2many('stock.picking.type', 'stock_picking_type_assortment_rel',
                                           string='Operation Type')
    complexity_assortment_team_type_ids = fields.One2many('combo.complexity.assortment.team.type',
                                                          'combo_assortment_team_type_id',
                                                          string='Complexity Assortment Team Types')
    maximum_lines = fields.Integer(string="Maximum Lines")

    @api.onchange('maximum_lines')
    def onchange_maximum_lines(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/03/25
            Task: Migration to v18 from v16
            Purpose: It will raise error when user will change the maximum lines, when stock pickings will be their in
                    selected team type
        """
        if self.complexity_assortment_team_type_ids:
                raise ValidationError(_("You cannot update Maximum Lines as it has transfers left to be validate"))