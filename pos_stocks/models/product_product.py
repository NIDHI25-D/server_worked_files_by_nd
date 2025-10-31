from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_loyalty_reward_products = fields.Boolean("Is reward lines products?")

    @api.model
    def _load_pos_data_fields(self, config_id):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/02/25
            Task: Migration to v18 from v16
            Purpose: This method is used to include field in js
        """
        params = super()._load_pos_data_fields(config_id)
        params += ['qty_available', 'virtual_available', 'outgoing_qty', 'type', 'is_loyalty_reward_products']
        return params
