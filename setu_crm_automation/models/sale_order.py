from odoo import api, fields, models


class Sale_Order(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: This method creates the sale.order from the New Quotation button of crm.lead and
                    modifies the state of crm.lead --> Qualified
        """
        res = super(Sale_Order, self).create(vals)
        res.opportunity_id.with_context(is_from_sale_order=True).stage_id = self.env.ref('crm.stage_lead2').id
        return res

    def action_confirm(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: This method is called when the sale.order of crm is confirmed and modifies the stage of crm
        """
        res = super(Sale_Order, self).action_confirm()
        if self.opportunity_id:
            if not self.opportunity_id.order_ids.filtered(lambda o: o.state != 'sale'):
                self.opportunity_id.with_context(is_from_sale_order=True).stage_id = self.env.ref('crm.stage_lead3').id
        return res

    def unlink(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: This method appears in the execution when the sale.order from crm is cancelled and the state of crm --> PROPOSITION
        """
        opportunity_lst = []
        for op in self:
            opportunity_lst.append(op.opportunity_id)
        res = super(Sale_Order, self).unlink()
        for op in opportunity_lst:
            if op and not op.order_ids.filtered(lambda o: o.state != 'cancel'):
                op.with_context(is_from_sale_order=True).stage_id = self.env.ref('crm.stage_lead3').id
        return res
