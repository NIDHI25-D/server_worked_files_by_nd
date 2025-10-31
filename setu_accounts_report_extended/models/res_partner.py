from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)
class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_view_overdue_moves(self):
        """
        Purpose: create an action for showing related landed cost.
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_account_moves_all")
        domain = [('account_id.reconcile', '=', True), '|', ('matching_number', '=', False),
                  ('matching_number', '=like', 'P%'), ('partner_id', '=', self.id)]
        views = [(self.env.ref('account.view_move_line_tree').id, 'list')]
        return dict(action, domain=domain, views=views)

    def _cron_execute_followup(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 03/03/25
            Task: Migration from V16 to V18 excludes the journal items from follow-up (Emailing debit balance automation. - development/Dev Testing.)
            Purpose: excludes the journal items from follow-up (Adding context to filter).
            during migration delete all follow-up level except First reminder email
        """
        context = self._context.copy() or {}
        context.update({'partner_follow_up': True, 'follow_up_email': True})
        super(ResPartner, self.with_context(context))._cron_execute_followup()

    def action_manually_process_automatic_followups(self):
        """
            Author: udit@setuconsulting
            Date: 14/12/23
            Task: Migration from V16 to V18 excludes the journal items from follow-up (Emailing debit balance automation. - development/Dev Testing.)
            Purpose: excludes the journal items from follow-up (Adding context to filter).
            odoo filtering followup_status == 'in_need_of_action', remove condition because send a mail to customers whose due period has not yet been exceeded
        """
        context = self._context.copy() or {}
        context.update({'partner_follow_up': True, 'follow_up_email': True})
        partners_with_missing_info = self.env['res.partner']
        for partner in self:
            # Skip partner with missing info.
            if partner._has_missing_followup_info():
                partners_with_missing_info |= partner
                continue

            partner.with_context(context)._execute_followup_partner()

        # If one or more partners are missing information, open a wizard listing them.
        if partners_with_missing_info:
            return partners_with_missing_info._create_followup_missing_information_wizard()

    def _get_followup_report(self, options):
        """
            Author: nidhi@setconsulting.com
            Date: 24/08/25
            Task: customer statement missing column { https://app.clickup.com/t/86dxby19n} comment==> https://app.clickup.com/t/86dxby19n?comment=90170149395014
            Purpose:when cron 'Account Report Followup; Execute followup' execute, customer_statement_report records
                 sent to customer in mail
        """
        if not self._context.get('follow_up_email'):
            return super(ResPartner, self)._get_followup_report(options)
        attachment_ids = options.setdefault('attachment_ids',self._get_invoices_to_print(options).message_main_attachment_id.ids)
        followup_report = self.env.ref('account_reports.customer_statement_report', raise_if_not_found=False)
        options['report_attachment_id'] = self._get_partner_account_report_attachment(followup_report).id
        attachment_ids.append(options['report_attachment_id'])

    def _cron_execute_followup_company(self):
        """
            Author: nidhi@setconsulting.com
            Date: 25/08/25
            Task: customer statement missing column { https://app.clickup.com/t/86dxby19n} comment==> https://app.clickup.com/t/86dxby19n?comment=90170149395014
            Purpose: send mail to customer if send_debit_balance_report checked in payment term
            odoo filtering followup_status == 'in_need_of_action', remove condition because send a mail to customers whose due period has not yet been exceeded
        """
        if not self._context.get('follow_up_email'):
            return super(ResPartner, self)._cron_execute_followup_company()
        followup_data = self._query_followup_data(all_partners=True)
        in_need_of_action = self.env['res.partner'].browse([d['partner_id'] for d in followup_data.values()])
        in_need_of_action_auto = in_need_of_action.filtered(lambda p: p.followup_line_id.auto_execute and p.followup_reminder_type == 'automatic' and p.property_payment_term_id and p.property_payment_term_id.send_debit_balance_report)
        customer = 0
        for partner in in_need_of_action_auto[:1000]:
            try:
                partner._execute_followup_partner()
                customer += 1
                _logger.info("=========================================No of partner mails sent for follow up ======== %s.", customer)
            except UserError as e:
                # followup may raise exception due to configuration issues
                # i.e. partner missing email
                partner._message_log(body=e)
                _logger.warning(e, exc_info=True)


    def _execute_followup_partner(self, options=None):
        """
            Author: nidhi@setconsulting.com
            Date: 26/08/25
            Task: customer statement missing column { https://app.clickup.com/t/86dxby19n} comment==> https://app.clickup.com/t/86dxby19n?comment=90170149395014
            Purpose: odoo filtering followup_status == 'in_need_of_action', remove condition because send a mail to customers whose due period has not yet been exceeded
        """
        if not self._context.get('follow_up_email'):
            return super(ResPartner, self)._execute_followup_partner(options=options)
        self.ensure_one()
        if options is None:
            options = {}
        if options.get('manual_followup', self._context.get('follow_up_email')):
            followup_line = self.followup_line_id or self._get_first_followup_level()

            if followup_line.create_activity:
                # log a next activity for today
                self.activity_schedule(
                    activity_type_id=followup_line.activity_type_id and followup_line.activity_type_id.id or self._default_activity_type().id,
                    note=followup_line.activity_note,
                    summary=followup_line.activity_summary,
                    user_id=(self._get_followup_responsible()).id
                )
            options['followup_line'] = followup_line
            self._update_next_followup_action_date(followup_line)

            self._get_followup_report(options)
            if not options.get('join_invoices', followup_line.join_invoices):
                report_attachment_id = options.get('report_attachment_id')
                options['attachment_ids'] = [report_attachment_id] if report_attachment_id else []

            self._send_followup(options)
            return True
        return False

    def _get_all_followup_contacts(self):
        """
            Author: nidhi@setconsulting.com
            Date: 26/08/25
            Task: customer statement missing column { https://app.clickup.com/t/86dxby19n} comment==> https://app.clickup.com/t/86dxby19n?comment=90170149395014
            Purpose: if self id not in res, it will add self id {if parent id of partner is not res it will add}
        """
        res = super(ResPartner, self)._get_all_followup_contacts()
        if self._context.get('follow_up_email'):
            return res | self
        return res