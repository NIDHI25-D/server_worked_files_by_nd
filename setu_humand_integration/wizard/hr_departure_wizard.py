# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import requests
import logging

_logger = logging.getLogger("Setu_Humand_Integration")


class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    def action_register_departure(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 19/02/25
            Task: Migration to v18 from v16
            Purpose: To archive employee account into humand.
        """
        super().action_register_departure()
        active_id = self.env['hr.employee'].browse(self.env.context.get('active_id', False))
        if active_id:
            employeeInternalId = active_id.work_email
            humand_access_token = self.env.company.humand_access_token or ''
            if employeeInternalId and humand_access_token:
                active_id.archive_employee_to_humand(humand_access_token, employeeInternalId)