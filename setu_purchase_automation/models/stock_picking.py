from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    container_type = fields.Selection(
        [('20_feet', '20 Feet'), ('40_feet', '40 Feet'), ('consolidated', 'Consolidated')], string="Container Type")
    container_qty_received = fields.Selection([('1', '1'), ('2', '2')], string="Quantity")
    containers_cubic_meters = fields.Float("Cubic meters")
    container_ref = fields.Char("Container Reference")
    location_id_usage = fields.Selection(related='location_id.usage')

    def button_validate(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: set received_date and extended_state of respective PO as per the condition when validating the transfer.
        """
        for rec in self:
            if rec.picking_type_id.code == 'incoming' and rec.purchase_id.waiting_for_expences:
                raise UserError(_("You can't Validate picking until the PO in the Waiting for Expenses"))
        res = super(StockPicking, self).button_validate()
        for rec in self:
            if res and rec.picking_type_id.code == 'incoming' and rec.purchase_id and rec.purchase_id.extended_state == 'counting':
                rec.purchase_id.update({'received_date': rec.date_done, 'extended_state': 'received'})
        return res

    def action_cancel(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: change received_date of corresponding PO as per the condition when cancel the transfer.
        """
        res = super(StockPicking, self).action_cancel()
        if res and self.purchase_id:
            self.purchase_id.update({'received_date': max(self.purchase_id.picking_ids.filtered(lambda x: x.date_done).mapped(
                'date_done')) if self.purchase_id.picking_ids.filtered(lambda x: x.date_done).mapped(
                'date_done') else datetime.now()})
        return res


# class StockImmediateTransfer(models.TransientModel):
#     _inherit = 'stock.immediate.transfer'
#
#     def process(self):
#         res = super(StockImmediateTransfer, self).process()
#         po = self.env['purchase.order'].search([('name', '=', self._context.get('default_origin'))])
#         if po and not po.picking_ids.filtered(lambda pick: pick.state != 'done'):
#             po.sudo().update({'received_date': max(po.picking_ids.mapped('date_done'))})
#             if po.extended_state == 'counting':
#                 po.sudo().update({'extended_state': 'received'})
#         return res
