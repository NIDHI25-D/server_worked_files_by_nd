# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, Command


class FollowupManualReminder(models.TransientModel):
    _inherit = 'account_followup.manual_reminder'
    _description = "Wizard for sending manual reminders to clients"

    def process_followup(self):
        """
            Author: udit@setuconsulting
            Date: 14/12/23
            Task: Migration from V16 to V18 excludes the journal items from follow-up (Emailing debit balance automation. - development/Dev Testing.)
            Purpose: excludes the journal items from follow-up (Adding context to filter).
        """
        super(FollowupManualReminder, self.with_context(partner_follow_up=True)).process_followup()
