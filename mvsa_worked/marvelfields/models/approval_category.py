# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    has_currency = fields.Selection(CATEGORY_SELECTION, string="Has Currency", default="no", required=True)
    has_payment_limit_date = fields.Selection(CATEGORY_SELECTION, string="Has payment limit date", default="no",
                                              required=True)
    has_bank_id = fields.Selection(CATEGORY_SELECTION, string="Has bank", default="no", required=True)
    has_payment_state = fields.Selection(CATEGORY_SELECTION, string="Has payment state", default="no", required=True)
    has_department_id = fields.Selection(CATEGORY_SELECTION, string="Department", default="no", required=True)
    has_job_id = fields.Selection(CATEGORY_SELECTION, string="Job Position", default="no", required=True)