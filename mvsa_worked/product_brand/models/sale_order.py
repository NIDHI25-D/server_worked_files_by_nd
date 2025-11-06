from odoo import models, fields,api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_tags_filter_view = fields.Many2many('crm.tag', 'sale_crm_tag_rel', 'sale_id', 'tag_id',string="Product Tags")

    @api.onchange('order_line')
    def onchange_order_line(self):
        """
            Authour: nidhi@setconsulting.com
            Date: 10/12/24
            Task: Migration from V16 to V18
            Purpose: This method is called when ordeline's crm tags are changed
        """
        res = super(SaleOrder, self).onchange_order_line()
        self.product_tags_filter_view = self.order_line.product_id.mapped('crm_tags_ids')
        return res
