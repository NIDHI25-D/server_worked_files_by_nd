# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ScoreConf(models.Model):
    _name = "score.conf"
    _description = "Score Conf"

    # Char Fields
    name = fields.Char(string="Rule")

    # Selection Fields
    calculation_based_on = fields.Selection(
        selection=[('price', 'Price'),
                       ('percentage', 'Percentage'),
                       ('quantity', 'Quantity')], required=True)
    calculation_formula = fields.Selection(
        selection=[('avg_monthly_sales', 'avg_monthly_sales'),
                       ('avg_monthly_refund', 'avg_monthly_refund'),
                       ('qty_invoice_paid', 'qty_invoice_paid'),
                       ('amt_invoice_paid', 'amt_invoice_paid'),
                       ('qty_invoice_due', 'qty_invoice_due'),
                       ('amt_invoice_due', 'amt_invoice_due'),
                       ('avg_payment_days', 'avg_payment_days')], required=1)

    # Relational Fields
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company")
    score_conf_line_price_ids = fields.One2many(
        comodel_name="score.conf.line.price",
        inverse_name="score_conf_id",
        string="Score Conf Line")
    score_conf_line_percentage_ids = fields.One2many(
        comodel_name='score.conf.line.percentage',
        inverse_name="score_conf_id", 
        string="Score Conf Line Percentage")
    score_conf_line_qty_ids = fields.One2many(
        comodel_name="score.conf.line.qty", 
        inverse_name="score_conf_id",
        string="Score Conf Line Qty")

    @api.constrains('score_conf_line_price_ids')
    def price_validations(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 02/12/2024
        Task: [1393] Setu Customer Rating v18
        Purpose: Price Validation
        :return: None
        """
        total_lines = self.score_conf_line_price_ids
        for line in total_lines:
            rules = line.sudo().search([('score_conf_id', '=', line.score_conf_id.id)])
            if rules.filtered(lambda rule: rule.id != line.id and rule.pre_score == line.pre_score):
                raise ValidationError(_('Same Pre-Score can not be applied to new rule.'))
            if line.from_price > line.to_price:
                raise ValidationError(_("'From Price' must be less than 'To Price'"))
            if rules.filtered(lambda rule: rule.id != line.id).filtered(
                    lambda rule: (rule.from_price < line.from_price
                                  and
                                  rule.to_price > line.to_price)
                                 or
                                 (rule.from_price > line.from_price
                                  and
                                  rule.to_price < line.to_price)
                                 or
                                 line.from_price <= rule.from_price <= line.to_price <= rule.to_price
                                 or
                                 rule.from_price <= line.from_price <= rule.to_price <= line.from_price):
                raise ValidationError(_("Rule's price range is conflicting with other rules."))

    @api.constrains('score_conf_line_percentage_ids')
    def percentage_validations(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 02/12/2024
        Task: [1393] Setu Customer Rating v18
        Purpose: Percentage Validation
        :return: None
        """
        total_lines = self.score_conf_line_percentage_ids
        for line in total_lines:
            rules = line.sudo().search([('score_conf_id', '=', line.score_conf_id.id)])
            if rules.filtered(lambda rule: rule.id != line.id and rule.pre_score == line.pre_score):
                raise ValidationError(_('Same Pre-Score can not be applied to new rule.'))
            if line.from_percentage > line.to_percentage:
                raise ValidationError(_("'From Percentage' must be less than 'To Percentage'"))
            if rules.filtered(lambda rule: rule.id != line.id).filtered(
                    lambda rule: rule.from_percentage < line.from_percentage
                                 and
                                 rule.to_percentage > line.to_percentage
                                 or
                                 rule.from_percentage > line.from_percentage
                                 and
                                 rule.to_percentage < line.to_percentage
                                 or
                                 line.from_percentage <= rule.from_percentage <= line.to_percentage <= rule.to_percentage
                                 or
                                 rule.from_percentage <= line.from_percentage <= rule.to_percentage <= line.from_percentage):
                raise ValidationError(_("Rule's price range is conflicting with other rules."))

    @api.constrains('score_conf_line_qty_ids')
    def qty_validations(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 02/12/2024
        Task: [1393] Setu Customer Rating v18
        Purpose: Quantity Validation
        :return: None
        """
        total_lines = self.score_conf_line_qty_ids
        for line in total_lines:
            rules = line.sudo().search([('score_conf_id', '=', line.score_conf_id.id)])
            if rules.filtered(lambda rule: rule.id != line.id and rule.pre_score == line.pre_score):
                raise ValidationError(_('Same Pre-Score can not be applied to new rule.'))
            if line.from_quantity > line.to_quantity:
                raise ValidationError(_("'From Quantity' must be less than 'To Quantity'"))
            if rules.filtered(lambda rule: rule.id != line.id).filtered(
                    lambda rule: rule.from_quantity < line.from_quantity
                                 and
                                 rule.to_quantity > line.to_quantity
                                 or
                                 rule.from_quantity > line.from_quantity
                                 and
                                 rule.to_quantity < line.to_quantity
                                 or
                                 line.from_quantity <= rule.from_quantity <= line.to_quantity <= rule.to_quantity
                                 or
                                 rule.from_quantity <= line.from_quantity <= rule.to_quantity <= line.from_quantity):
                raise ValidationError(_("Rule's price range is conflicting with other rules."))
