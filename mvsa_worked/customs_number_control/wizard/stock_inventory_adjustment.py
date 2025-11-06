from odoo import fields, models, _


class StockInventoryAdjustmentName(models.TransientModel):
    _inherit = 'stock.inventory.adjustment.name'

    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        string='Attachment',
        required=True)

    def action_apply(self):
        """
                    Authour: nidhi@setconsulting.com
                    Date: 21/08/25
                    Task: Inventory Adjustment - attachment field {https://app.clickup.com/t/86dxedhg7}
                    Purpose: to add attachment in chatter when inventory adjustment created [migrate from v16]
        """
        return super(StockInventoryAdjustmentName, self.with_context(attachment_ids=self.attachment_ids.ids)).action_apply()
