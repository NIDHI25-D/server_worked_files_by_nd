from odoo import api, fields, models, Command


class FollowupManualReminder(models.TransientModel):
    _inherit = 'account_followup.manual_reminder'

    def default_get(self, fields_list):
        """
            Author: jay.garach@setuconsulting.com
            Date: 01/01/25
            Task: Migration from V16 to V18 (Follow-up button from Due invoices (Partner))
            Purpose: This method will add : current parent's child partner when send mail child boolean is True.
            - This is modified as compare to V16 because in V16 there was a button : Follow UP and now updated to Send.
        """
        defaults = super().default_get(fields_list)
        partner =  self.env['res.partner'].browse(defaults.get('partner_id'))
        child_id = partner.search([('id', 'child_of', partner.id), ('send_mail_child', '=', True)])
        defaults.update(
            email_recipient_ids=[(6, 0, partner.ids + partner.parent_id.ids + child_id.ids)],
        )
        return defaults







