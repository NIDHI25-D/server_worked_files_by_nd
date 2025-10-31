from odoo import fields, models, api


class StockMoveLine(models.Model):
    _name = 'stock.move.line'
    _inherit = ['stock.move.line', 'mail.thread']

    # Task: Migration from V16 to V18 (added from customs_number_control)*#*
    customs_number = fields.Char('Custom Number', readonly=True)
    remaining_qty = fields.Float('Remaining Quantity', readonly=True)
    reserve_used_qty = fields.Float('Reserve Used', readonly=True)
    attachment_ids = fields.Many2many('ir.attachment')

    @api.model_create_multi
    def create(self, vals_list):
        """
            Authour: nidhi@setconsulting.com
            Date: 21/08/25
            Task: Inventory Adjustment - attachment field {https://app.clickup.com/t/86dxedhg7}
            Purpose: to add attachment in chatter when inventory adjustment created [migrate from v16]
        """
        for vals in vals_list:
            if vals.get('quantity'):
                vals['reserve_used_qty'] = vals.get('quantity', 0)
        res = super(StockMoveLine, self).create(vals_list)
        if res and self._context.get('attachment_ids'):
            for rec in res:
                rec.message_post(attachment_ids=self._context.get('attachment_ids'))
        return res
