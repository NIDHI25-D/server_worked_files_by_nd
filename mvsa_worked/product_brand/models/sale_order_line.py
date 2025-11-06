from odoo import models, fields,api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_tags_field = fields.Many2many('crm.tag','saleline_crm_tag_rel','sale_id','tag_id',string="Product Tags")

    @api.onchange('product_id')
    def _onchange_product_id_warning(self):
        """
            Authour: nidhi@setconsulting.com
            Date: 10/12/24
            Task: Migration from V16 to V18
            Purpose: This method is called when ordeline's product_id are changed it will set the tags as per mentioned in products
        """
        res = super(SaleOrderLine, self)._onchange_product_id_warning()
        if self.product_id:
            self.product_tags_field = self.product_id.mapped('crm_tags_ids')
        return res
