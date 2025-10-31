from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _load_pos_data_fields(self, config_id):
        """
            Author: jay.garach@setuconsulting.com
            Date:  10/12/24
            Task: Migration from V16 to V18
            Purpose: This method is used to include filed minimum_price in js
        """
        result = super()._load_pos_data_fields(config_id)
        result.append('minimum_price')
        return result
