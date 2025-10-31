from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    purchase_price_base = fields.Float(string='Cost Base', copy=False)
    purchase_price = fields.Float(string='Cost', copy=False)
    picking_ids = fields.Many2many(comodel_name='stock.picking', string='Pickings', copy=False)

    def action_view_pickings(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 05/12/24
            Task: Migration from V16 to V18
            Purpose: to show related pickings.
        """
        self.ensure_one()
        picking_ids = self.picking_ids
        result = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        if picking_ids:
            result['domain'] = [('id', 'in', picking_ids.ids)]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
