from odoo import api, fields, models


class LoyaltyReward(models.Model):
    _inherit = 'loyalty.reward'

    def _create_missing_discount_line_products(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/02/25
            Task: Migration to v18 from v16
            Purpose: If discount_line_product_id in rewards then it will set the True in is_loyalty_reward_product = True
        """
        res = super(LoyaltyReward, self)._create_missing_discount_line_products()
        for reward in self:
            reward_product = reward.discount_line_product_id
            if reward_product:
                reward_product.is_loyalty_reward_products = True
