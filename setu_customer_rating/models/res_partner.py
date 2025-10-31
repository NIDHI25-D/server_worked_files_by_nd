# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Integer Fields
    total_score = fields.Integer(
        string="Score",
        company_dependent=True)
    # Relational Fields
    rating = fields.Many2one(
        comodel_name="customer.rating",
        string="Customer Rating",
        company_dependent=True)
    customer_score_id = fields.Many2one(
        comodel_name="customer.score",
        string="Customer Score",
        company_dependent=True)

    def view_to_customer_score(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 02/12/2024
        Task: [1393] Setu Customer Rating v18
        Purpose: View customer score
        :return:
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'customer.score',
            'view_mode': 'form',
            'res_id': self.customer_score_id.id,
            'target': 'current',
        }

