from odoo import models


class LoyaltyReward(models.Model):
    _inherit = 'loyalty.reward'

    def _get_discount_product_values(self):
        res = super()._get_discount_product_values()
        config = self.env['ir.config_parameter'].get_param('setu_discount_and_loyalty_enhancment.df_unspsc_code_id')
        for product in res:
            product.update({'service_policy': 'ordered_prepaid', 'unspsc_code_id': int(config)})
        return res

    def write(self, vals):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/12/23
            Task: Migration from V16 to V18
            Purpose: active the product.product after loyalty program is archived
        """
        res = super().write(vals)
        if 'active' in vals:
            self.reward_product_id.action_unarchive()
        return res
