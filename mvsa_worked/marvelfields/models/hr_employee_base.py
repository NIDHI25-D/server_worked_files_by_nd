# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools, _
import datetime


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    vat = fields.Char(string="VAT")
    curp = fields.Char(string="CURP")
    nss = fields.Char(string="NSS")
    incom_date = fields.Date(string="Incom Date")
    antiquity = fields.Text(string="Antiquity", compute='_get_antiquity')

    def _get_antiquity(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 01/01/25
            Task: Migration from V16 to V18
            Purpose: Set an antiquity in years as per the incom_date.
        """
        for record in self:
            antiquity = "0"
            if record.incom_date:
                age = (datetime.datetime.now() - datetime.datetime.strptime(str(record.incom_date),
                                                                            "%Y-%m-%d")).days / 365.25
                antiquity = float("{0:.2f}".format(age))
            record.antiquity = str(antiquity) + ' ' + _('Years')
