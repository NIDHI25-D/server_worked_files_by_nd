from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'mail.activity'

    def _action_done(self, feedback=False, attachment_ids=None):
        """
            Author: jay.garach@setuconsulting.com
            Date: 02/01/25
            Task: Migration from V16 to V18
            Purpose: To set the is mark done in to sale order from sale order activities.
        """
        for rec in self:
            if rec.res_model == 'sale.order':
                order_id = self.env['sale.order'].browse(rec.res_id)
                order_id.is_mark_done = True if order_id else False
        return super()._action_done(feedback=feedback, attachment_ids=attachment_ids)
