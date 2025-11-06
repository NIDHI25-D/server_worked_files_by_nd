from odoo import _, models, api, tools


class AccountMoveSendWizard(models.TransientModel):
    _inherit = 'account.move.send.wizard'

    @api.model
    def _get_default_mail_partner_ids(self, move, mail_template, mail_lang):
        """
        @name: nidhi@setuconsulting.com ||@date:09/10/2025 || @task:12985
        @purpose: This method is overridden to set the partner IDs as follows:
                - The main customer (partner_id) associated with the invoice.
                - The child partners of the main customer with the type 'followup' and the flag 'send_mail_child' set to True.
        """
        partners = self.env['res.partner'].with_company(move.company_id)

        # Retrieve the main partner (customer) from the move
        partner_id = move.partner_id

        # Add the main partner (customer) to the partners list
        partners |= partner_id

        child_partners = partner_id.child_ids.filtered(
            lambda p: p.type == 'followup' and p.send_mail_child
        )
        partners |= child_partners

        if mail_template.email_to:
            email_to = self._get_mail_default_field_value_from_template(mail_template, mail_lang, move, 'email_to')
            for mail_data in tools.email_split(email_to):
                partners |= partners.find_or_create(mail_data)

        if mail_template.email_cc:
            email_cc = self._get_mail_default_field_value_from_template(mail_template, mail_lang, move, 'email_cc')
            for mail_data in tools.email_split(email_cc):
                partners |= partners.find_or_create(mail_data)

        if mail_template.partner_to:
            partner_to = self._get_mail_default_field_value_from_template(mail_template, mail_lang, move, 'partner_to')
            partner_ids = mail_template._parse_partner_to(partner_to)
            partners |= self.env['res.partner'].sudo().browse(partner_ids).exists()

        # Ensure that only partners with an email are returned
        return partners.filtered('email')
