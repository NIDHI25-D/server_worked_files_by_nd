from odoo import api, models, fields, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        """
              Author: jay.garach@setuconsulting.com
              Date: 16/12/23
              Task: Migration from V16 to V18
              Purpose: discount line set as per invoiced quantity
        """
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res.update({'is_reward_line': self.is_reward_line, 'reward_id': self.reward_id.id})
        return res
