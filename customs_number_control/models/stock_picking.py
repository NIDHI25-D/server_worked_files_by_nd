from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # def _action_done(self):
    #     for rec in self:
    #         for move_line in rec.move_line_ids:
    #             move_line.reserve_used_qty = move_line.reserved_uom_qty
    #     return super()._action_done()
