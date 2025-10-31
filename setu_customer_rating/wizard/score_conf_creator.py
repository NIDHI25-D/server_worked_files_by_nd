# -*- coding: utf-8 -*-
from odoo import fields, models


class ModelName(models.TransientModel):
    _name = "score.conf.creator"
    _description = "Score Conf Creator"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company", required=1)

    def confirm(self):
        if self.env['score.conf'].search([('company_id', '=', self.company_id.id)]):
            action = self.env.ref('setu_customer_rating.score_conf_creator_act_window').read()[0]
            action['view_id'] = (self.env.ref('setu_customer_rating.score_conf_creator_company_exists_form_view').id,
                                 'score_conf_exists_form_warning')
            action['views'] = [(
                self.env.ref('setu_customer_rating.score_conf_creator_company_exists_form_view').id, 'form')]
            return action

        avg_monthly_sales = self.env['score.conf'].search([('calculation_formula', '=', 'avg_monthly_sales')], limit=1)

        avg_monthly_refund = self.env['score.conf'].search([('calculation_formula', '=', 'avg_monthly_refund')],
                                                           limit=1)
        qty_invoice_paid = self.env['score.conf'].search([('calculation_formula', '=', 'qty_invoice_paid')], limit=1)
        amt_invoice_paid = self.env['score.conf'].search([('calculation_formula', '=', 'amt_invoice_paid')], limit=1)
        qty_invoice_due = self.env['score.conf'].search([('calculation_formula', '=', 'qty_invoice_due')], limit=1)
        amt_invoice_due = self.env['score.conf'].search([('calculation_formula', '=', 'amt_invoice_due')], limit=1)
        avg_payment_days = self.env['score.conf'].search([('calculation_formula', '=', 'avg_payment_days')], limit=1)
        confs = (
                avg_monthly_sales + avg_monthly_refund + qty_invoice_paid + amt_invoice_paid + qty_invoice_due + amt_invoice_due + avg_payment_days)

        for conf in confs:
            new_conf = conf.copy()
            new_conf.company_id = self.company_id
            for line in conf.score_conf_line_percentage_ids:
                new_line = line.copy()
                new_line.score_conf_id = new_conf
            for line in conf.score_conf_line_price_ids:
                new_line = line.copy()
                new_line.score_conf_id = new_conf
            for line in conf.score_conf_line_qty_ids:
                new_line = line.copy()
                new_line.score_conf_id = new_conf

        self.env['customer.rating'].create({
            'company_id': self.company_id.id,
            'from_score': 0,
            'to_score': 69,
            'rating': 'C'
        })
        self.env['customer.rating'].create({
            'company_id': self.company_id.id,
            'from_score': 70,
            'to_score': 79,
            'rating': 'B'
        })
        self.env['customer.rating'].create({
            'company_id': self.company_id.id,
            'from_score': 80,
            'to_score': 89,
            'rating': 'A'
        })

        self.env['customer.rating'].create({
            'company_id': self.company_id.id,
            'from_score': 90,
            'to_score': 100,
            'rating': 'AAA'
        })
