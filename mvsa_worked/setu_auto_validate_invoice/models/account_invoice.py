from odoo import models, fields, api, _, SUPERUSER_ID
import logging
_logger = logging.getLogger("auto_send_invoices_to_sign")
_logger = logging.getLogger("ir_cron_module_edi_sign_invoice_payments")
from datetime import date


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        if self._context.get('is_from_pos_order'):
            return self.browse()
        res = super(AccountInvoice, self)._post(soft=soft)
        return res

    # def write(self,vals):
    #     if vals.get('l10n_mx_edi_cfdi_uuid') and self.payment_ids and self.move_type == 'entry':
    #         self.payment_ids.mail_sent()
    #     return super().write(vals)

    # def invoice_mail_data(self):
    #     invoice_sent_data = self.action_invoice_sent()
    #     context_data = invoice_sent_data.get('context')
    #     context_data.update({'active_ids': self.ids})
    #     wizard_id = self.env['account.invoice.send'].with_context(context_data). \
    #         create({'template_id': context_data.get('default_template_id'),
    #                 'composition_mode': context_data.get('default_composition_mode'),
    #                 'model': context_data.get('default_model'),
    #                 'res_id': context_data.get('default_res_id')
    #                 })
    #     partners = self.partner_id.child_ids.filtered(lambda x: x.type == 'followup').ids if self.partner_id.child_ids else []
    #     partners.append(self.partner_id.id)
    #     wizard_id.onchange_template_id()
    #     wizard_id.partner_ids = [(6, 0, partners)]
    #     wizard_id.with_user(SUPERUSER_ID)._send_email()

    def _generate_and_send(self, force_synchronous=True, allow_fallback_pdf=True, **custom_settings):
        """
            Author: siddharth@setuconsulting.com
            Date: 14/04/25
            Task: The return credit note is automatically signed
            Purpose: For not apply the invoice payments when disable_inv_sign_check is selected.
        """

        disable_inv_sign_check = self.env['ir.config_parameter'].sudo().get_param(
            'setu_auto_validate_invoice.disable_inv_automatic_sign') or False
        documents = hasattr(self.partner_id, 'disable_inv_automatic_sign') and self.filtered(
            lambda doc: not doc.partner_id.disable_inv_automatic_sign) or False
        if (bool(disable_inv_sign_check) or not documents) or self.move_type == 'out_refund' or self.pos_order_ids:
            return self.browse()
        res = super()._generate_and_send(force_synchronous=force_synchronous,allow_fallback_pdf=allow_fallback_pdf,**custom_settings)
        return res

    def _l10n_mx_edi_add_invoice_cfdi_values(self, cfdi_values):
        """
            Author: siddharth@setuconsulting.com
            Date: 15/05/25
            Task: mvsa migration
            Purpose: override currency conversion rate as per calculated l10n_mx_currency_rate
        """
        super()._l10n_mx_edi_add_invoice_cfdi_values(cfdi_values)
        if hasattr(self, 'l10n_mx_currency_rate') and self.currency_id.name != 'MXN':
            cfdi_values['tipo_cambio'] = self.l10n_mx_currency_rate

    def _cron_auto_send_invoices_and_sign_process(self, job_count=5,exclude_ids=None):
        """
            Author: siddharth@setuconsulting.com
            Date: 09/07/25
            Task: mvsa migration as per the task - https://app.clickup.com/t/86dx49f9w
            Purpose: creates new scheduled action to auto sign process for invoices.
        """

        limit = job_count
        _logger.info(f"-------start to auto send invoice to sign----------")
        exclude_ids = exclude_ids or []
        _logger.info(f"-------Exclude Ids: {exclude_ids} from the _cron_auto_send_invoices_and_sign_process ----------")

        without_sent_invoice_ids = self.env['account.move'].search(
            [('state','=','posted'), ('l10n_mx_edi_cfdi_uuid', '=', False), ('move_type', 'in', ['out_invoice', 'out_refund', 'out_receipt']),
             ('id', 'not in', exclude_ids)],
            limit=limit, order="id desc"
        )
        _logger.info(f"-------without_sent_invoice_ids Ids: {without_sent_invoice_ids} from the _cron_auto_send_invoices_and_sign_process ----------")
        if not without_sent_invoice_ids:
            return

        for without_sent_invoice_id in without_sent_invoice_ids:
            try:
                wizard_data = without_sent_invoice_id.action_invoice_sent()
                # current_account = self.env[wizard_data.get('context').get('active_model')].browse(wizard_data.get('context').get('active_ids'))
                self.env['account.move.send.wizard'].with_context(wizard_data['context']).create({}).action_send_and_print()
                _logger.info(f"-------send invoice{without_sent_invoice_id.name} to sign----------")
            except Exception as e:
                _logger.exception("Error auto-signing invoice %s: %s", without_sent_invoice_id.name, e)

    @api.depends('l10n_mx_edi_invoice_document_ids.state')
    def _compute_l10n_mx_edi_update_payments_needed(self):
        """
        Authour: nidhi@setconsulting.com
        Date: 14/07/25
        Task: Payments are not signined automatically { https://app.clickup.com/t/86dx5pqmk }
        Purpose:This method is overwrite with the point of adding for loop to overcome the sign payment of the invoices
        """
        for invo in self:
            payments_diff = invo._origin \
                .with_context(bin_size=False) \
                ._l10n_mx_edi_cfdi_invoice_get_payments_diff()
            for move in invo:
                move.l10n_mx_edi_update_payments_needed = bool(
                    move in payments_diff['to_remove']
                    or move in payments_diff['need_update']
                    or payments_diff['to_process']
                )

    def edi_sign_invoice_payments(self):
        """
           Authour: nidhi@setconsulting.com
           Date: 14/07/25
           Task: Payments are not signined automatically { https://app.clickup.com/t/86dx5pqmk }
           Purpose: Created the cron which is used to sign the invoice payments when the payment is oartially paid or paid
           --The flow is once the Pay is either partial or paid than this cron will execute the flow -->Update Payments->force CFDI methods
           --Here limit of 20 is given for the While loop and 50 is given for the domain search process. It will work for 50 ids
        """
        limit = 10
        all_filtered_moves = []
        checked_ids = []
        batch_size = 50

        while len(all_filtered_moves) < limit:
            domain = [
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('l10n_mx_edi_cfdi_uuid', '!=', False),
                ('id', 'not in', checked_ids),
                ('create_date', '>', '2025-01-01'),
                ('journal_id', '!=', 253),
            ]
            batch_moves = self.search(domain, order='id desc', limit=batch_size).filtered(lambda x : x.l10n_mx_edi_payment_policy == 'PPD')

            if not batch_moves:
                break  # No more records to search

            checked_ids += batch_moves.ids

            filtered_batch = [move for move in batch_moves if move.l10n_mx_edi_update_payments_needed]

            all_filtered_moves += filtered_batch

        if not all_filtered_moves:
            _logger.info("Edi Sign Invoice Payments Cron: No matching invoices found.")
            return True

        _logger.info(f"Edi Sign Invoice Payments Cron: Processing {len(all_filtered_moves)} invoices")

        for count, move in enumerate(all_filtered_moves, start=1):
            move.l10n_mx_edi_cfdi_invoice_try_update_payments()
            _logger.info(f"PPD Invoice: {move.name}")
            _logger.info(f"Processed invoice {move.id}-{move.name} [{count} of {len(all_filtered_moves)}]")

        return True


