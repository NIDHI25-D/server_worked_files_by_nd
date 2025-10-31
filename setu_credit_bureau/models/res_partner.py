# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import re


class ResPartner(models.Model):
    _inherit = "res.partner"


    """EM section fields"""

    identifier2 = fields.Char(string="Identifier", size=2)
    dun_number = fields.Char(string="Dun number", size=10)
    name1 = fields.Char(string="Name 1", size=30)
    name2 = fields.Char(string="Name 2", size=30)
    last_name = fields.Char(string="Last Name", size=25)
    mother_last_name = fields.Char(string="Mother's Last Name", size=25)
    banxico_qualification = fields.Char(string="Banxico Qualification", size=2)
    address2 = fields.Char(string="Address 2", size=40)
    extension = fields.Char(string="Extension", size=8)
    fax = fields.Char(string="Fax", size=11)
    foreign_state = fields.Char(string="Foreign state", size=40)
    consolidation_code = fields.Char(string="Consolidation code", size=8)
    filler2 = fields.Char(string="Filler", size=87)

    """AC Segment fields"""

    ac_name1 = fields.Char(string="Name 1", size=30)
    ac_name2 = fields.Char(string="Name 2", size=30)
    ac_last_name = fields.Char(string="Last Name", size=25)
    ac_mother_last_name = fields.Char(string="Mother's Last Name", size=25)
    percent = fields.Char(string="Percent", size=2)
    ac_address2 = fields.Char(string="Address 2", size=40)
    ac_customer_type = fields.Char(string="Customer type", size=1)

    """CR Segment fields"""

    debt_discount = fields.Char(string="Debt discount", size=20)
    observations = fields.Char(string="Observations", size=4)
    liquidation_date = fields.Char(string="Liquidation date", size=8)
    datio_in_solutum = fields.Char(string="Datio In Solutum", size=20)
    debt_condonation = fields.Char(string="Debt Condonation", size=20)
    special_credit = fields.Char(string="Special Credit", size=1)

    """DE Segment fields"""

    contract = fields.Char(string="Contract", size=25)

    """AV Segment fields"""

    av_name1 = fields.Char(string="Name 1", size=30)
    av_name2 = fields.Char(string="Name 2", size=30)
    av_last_name = fields.Char(string="Last Name", size=25)
    av_mother_last_name = fields.Char(string="Mother's Last Name", size=25)
    av_address2 = fields.Char(string="Address 2", size=40)
    av_customer_type = fields.Char(string="Customer type", size=1)

    """Credit bureau phase 2 fields"""

    credit_bureau_report = fields.Boolean(string="Credit Bureau Report")
    credit_bureau_report_company_type = fields.Selection(string='Credit Bureau Report Company Type',
                                                         selection=[('endorser', 'Endorser'),
                                                                    ('shareholder', 'Shareholder')])
    contact_related_id = fields.Many2one("res.partner", string="Contact Related")
    shareholder_contact_related_id = fields.Many2one("res.partner", string="Shareholder Contact Related")
    endorser_contact_related_id = fields.Many2one("res.partner", string="Endorser Contact Related")

    def write(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 28/02/25
            Task: Migration to v18 from v16
            Purpose: fix the issue as write in create and write to set endarsor or shareholder customer to it's related partner instead of onchange.
        """
        res = super(ResPartner, self).write(vals)
        if vals.get('contact_related_id', False) or vals.get('credit_bureau_report_company_type', False):
            endorser_contact_related_id = self.search([('endorser_contact_related_id', '=', self.id)])
            if endorser_contact_related_id:
                endorser_contact_related_id.write({'endorser_contact_related_id': False})
            shareholder_contact_related_id = self.search([('shareholder_contact_related_id', '=', self.id)])
            if shareholder_contact_related_id:
                shareholder_contact_related_id.write({'shareholder_contact_related_id': False})
            if self.contact_related_id and self.credit_bureau_report_company_type == 'endorser':
                self.contact_related_id.write({'endorser_contact_related_id': self.id})
            elif self.contact_related_id and self.credit_bureau_report_company_type == 'shareholder':
                self.contact_related_id.write({'shareholder_contact_related_id': self.id})
        return res

    @api.model_create_multi
    def create(self, vals_list):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 28/02/25
            Task: Migration to v18 from v16
            Purpose: fix the issue as write in create and write to set endarsor or shareholder customer to it's related partner instead of onchange.
        """
        res = super(ResPartner, self).create(vals_list)
        for record in res:
            if record.contact_related_id and record.credit_bureau_report_company_type == 'endorser':
                record.contact_related_id.write({'endorser_contact_related_id': record.id})
            if record.contact_related_id and record.credit_bureau_report_company_type == 'shareholder':
                record.contact_related_id.write({'shareholder_contact_related_id': record.id})
        return res
