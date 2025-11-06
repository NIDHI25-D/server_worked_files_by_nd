# -*- coding: utf-8 -*-

from odoo import api, fields, models, _,tools


class ApprovalRequest(models.Model):
	_inherit = 'approval.request'

	currency_id = fields.Many2one('res.currency', string="Currency")
	payment_limit_date = fields.Date(string="Payment limit date")
	has_currency = fields.Selection(related="category_id.has_currency")
	has_payment_limit_date = fields.Selection(related="category_id.has_payment_limit_date")
	bank_id = fields.Many2one('account.journal', string="Bank", domain=[('type','=','bank')])
	payment_description = fields.Text(string="Payment Description")
	payment_state = fields.Selection([('paid','Paid'),('unpaid','Unpaid')],string="Payment State")
	has_bank_id = fields.Selection(related="category_id.has_bank_id")
	has_payment_state = fields.Selection(related="category_id.has_payment_state")
	has_department_id = fields.Selection(related="category_id.has_department_id")
	has_job_id = fields.Selection(related="category_id.has_job_id")
	department_id = fields.Many2one('hr.department', string='Department')
	job_id = fields.Many2one('hr.job', string="Job Position")