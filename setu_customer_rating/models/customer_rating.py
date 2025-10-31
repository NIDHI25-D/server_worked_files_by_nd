# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CustomerRating(models.Model):
    _name = "customer.rating"
    _rec_name = 'rating'
    _description = "Customer Rating"

    # Char Fields
    rating = fields.Char(required=True, string="Rating")

    # Integer Fields
    from_score = fields.Integer(required=True, string="From Score")
    to_score = fields.Integer(required=True, string="To Score")

    # Relational Fields
    company_id = fields.Many2one(comodel_name="res.company", string="Company")

    @api.constrains('from_score', 'to_score', 'rating')
    def validations(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 27/12/2024
        Task: [1393] Setu Customer Rating v18
        Purpose: Added customer rating validation
        :return:
        """
        rules = self.sudo().search([('company_id', '=', self.company_id.id)])
        if rules.filtered(
                lambda rule: rule.id != self.id and rule.rating == self.rating and rule.company_id == self.company_id):
            raise ValidationError(_('Same Rating can not be applied to new rule for the same company.'))
        if rules.filtered(lambda rule: rule.id != self.id).filtered(
                lambda rule: rule.company_id == self.company_id
                             and rule.from_score < self.from_score
                             and rule.to_score > self.to_score
                             or rule.from_score > self.from_score
                             and rule.to_score < self.to_score
                             or self.from_score <= rule.from_score <= self.to_score <= rule.to_score
                             or rule.from_score <= self.from_score <= rule.to_score <= self.from_score):
            raise ValidationError(_("Rule's price range is conflicting with other rules."))
