from odoo import fields, models, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    # @api.model
    # def _get_partner_id_for_valuation_lines(self):
    #     res = super(StockMove, self)._get_partner_id_for_valuation_lines()
    #     for move in self:
    #         if not move.picking_id and move.repair_id:
    #             return move.partner_id.id if not move.repair_id.address_id else move.repair_id.address_id.id
    #     return res
