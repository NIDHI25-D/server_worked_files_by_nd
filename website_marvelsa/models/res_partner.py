from odoo import models, fields, api
from datetime import datetime


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_purchases_goal = fields.Monetary(string="Customer purchases goal")
    customer_monthly_purchases = fields.Monetary(string="Customer monthly purchases", compute="_compute_monthly_purchases")
    fulfillment_percent = fields.Float(string="Fulfillment percent")
    electronic_wallet_purchase_goals = fields.Monetary(string="Electronic wallet when achieved the purchase goals")

    def _compute_monthly_purchases(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 11/03/25
            Task: Migration to v18 from v16
            Purpose: set the field value Customer monthly purchases, and this method are comes everytime as it in non stored.
        """
        start_date = datetime.today().replace(day=1).date()
        end_date = datetime.today().replace(day=28).date()
        for records in self:
            invoice_sum = sum(records.invoice_ids.filtered(lambda
                                                               x: x.move_type == "out_invoice" and x.state == 'posted' and x.invoice_date >= start_date and x.invoice_date <= end_date).mapped(
                'amount_total_signed'))
            credit_note_sum = sum(records.invoice_ids.filtered(lambda
                                                               x: x.move_type == "out_refund" and x.state == 'posted' and x.invoice_date >= start_date and x.invoice_date <= end_date).mapped(
            'amount_total_signed'))

            records.customer_monthly_purchases = invoice_sum + credit_note_sum
            if records._context.get('website_id') and records.customer_monthly_purchases and records.customer_purchases_goal > 0.0:
                records.fulfillment_percent = (records.customer_monthly_purchases / records.customer_purchases_goal) * 100
            elif records.customer_monthly_purchases and records.customer_purchases_goal > 0.0 and not records._context.get('website_id'):
                records.fulfillment_percent = (records.customer_monthly_purchases / records.customer_purchases_goal)
            elif records.customer_monthly_purchases and records.customer_purchases_goal <= 0.0:
                records.fulfillment_percent = 0.0

    @api.onchange('customer_purchases_goal')
    def onchange_customer_purchases_goal(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 11/03/25
            Task: Migration to v18 from v16
            Purpose: called the method to set the values of the field when Customer purchases goal is changed.
        """
        self._compute_monthly_purchases()
