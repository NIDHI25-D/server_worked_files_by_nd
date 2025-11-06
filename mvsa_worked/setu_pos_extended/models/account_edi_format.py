from odoo import models, fields, api
# from odoo.addons.account_edi_extended.models.account_edi_document import DEFAULT_BLOCKING_LEVEL
from psycopg2 import OperationalError
from datetime import datetime
import logging
import pytz

_logger = logging.getLogger(__name__)

# removed in 18.
# class AccountEdiFormat(models.Model):
#     _inherit = 'account.edi.format'
#
#     def _l10n_mx_edi_get_invoice_cfdi_values(self, move):
#         """
#         Added By : Ravi Kotadiya
#         Added On : Dec-23-2021
#         Use : To use the zip of supplier For Invoice Approval instead of company partner zip
#         :param move:
#         :return:
#         """
#         res = super(AccountEdiFormat, self)._l10n_mx_edi_get_invoice_cfdi_values(move)
#         if move.pos_order_ids:
#             pos_config_id = move.pos_order_ids[0].config_id
#             if pos_config_id.approval_partner_for_invoice.tz:
#                 res.update({'cfdi_date': datetime.combine(move.invoice_date, datetime.now(pytz.timezone(pos_config_id.approval_partner_for_invoice.tz)).time()).strftime('%Y-%m-%dT%H:%M:%S')})
#             if pos_config_id and pos_config_id.approval_partner_for_invoice and pos_config_id.approval_partner_for_invoice.zip:
#                 res.update({'supplier': pos_config_id.approval_partner_for_invoice,
#                             'issued_address': pos_config_id.approval_partner_for_invoice})
#         return res

# no need to this in base not used it.
# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     def _l10n_mx_edi_add_invoice_cfdi_values(self, cfdi_values):
#         """
#             Author: siddharth.vasani@setuconsulting.com
#             Date: 21/03/25
#             Task: Migration to v18 from v16
#             Purpose: EXTENDS invoice cfdi values to add custom --> fecha, supplier, issued_address
#         """
#
#         super()._l10n_mx_edi_add_invoice_cfdi_values(cfdi_values)
#         for move in self:
#             if move.pos_order_ids:
#                 pos_config_id = move.pos_order_ids[0].config_id
                # if pos_config_id.approval_partner_for_invoice.tz:
                #     cfdi_values.update({'fecha': datetime.combine(move.invoice_date, datetime.now(pytz.timezone(pos_config_id.approval_partner_for_invoice.tz)).time()).strftime('%Y-%m-%dT%H:%M:%S')})
                # if pos_config_id and pos_config_id.approval_partner_for_invoice and pos_config_id.approval_partner_for_invoice.zip:
                #     cfdi_values.update({'supplier': pos_config_id.approval_partner_for_invoice,
                #                         'issued_address': pos_config_id.approval_partner_for_invoice})
