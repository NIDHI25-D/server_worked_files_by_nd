
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
from codecs import BOM_UTF8

from odoo import _, api, models, fields, Command

from lxml import etree

BOM_UTF8U = BOM_UTF8.decode('UTF-8')
CFDI_SAT_QR_STATE = {
    'No Encontrado': 'not_found',
    'Cancelado': 'cancelled',
    'Vigente': 'valid',
}
# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',  # Customer Invoice
    'in_invoice': 'in_refund',  # Vendor Bill
    'out_refund': 'out_invoice',  # Customer Credit Note
    'in_refund': 'in_invoice',  # Vendor Credit Note
}
import logging

_logger = logging.getLogger(__name__)
MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')
CFDI_XSLT_CADENA = 'l10n_mx_edi/data/%s/cadenaoriginal.xslt'


class AccountMove(models.Model):
    _inherit = 'account.move'

    move_name = fields.Char(string='Journal Entry Name', readonly=True, default=False, copy=False)
    move_from_attachment = fields.Boolean('Move from attachment',default=False)

    def _l10n_mx_edi_get_xml(self):
        for inv in self:
            node_sello = 'Sello'
            certificate_ids = inv.company_id.l10n_mx_edi_certificate_ids
            certificate_id = certificate_ids.sudo().get_valid_certificate()
            tree = inv.l10n_mx_edi_get_xml_etree(inv.l10n_mx_edi_cfdi)
            cadena = self.l10n_mx_edi_generate_cadena(CFDI_XSLT_CADENA % '3.3', tree)
            tree.attrib[node_sello] = certificate_id.sudo().get_encrypted_cadena(cadena)
            return {'cfdi': etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')}

    def generate_xml_attachment(self, xml):
        self.ensure_one()
        fname = ("%s-%s-MX-Bill-%s.xml" % (
            self.journal_id.code, self.ref,
            self.company_id.partner_id.vat or '')).replace('/', '')
        uuid = self.env['attach.xmls.wizard'].get_xml_uuid(xml)
        data_attach = {
            'name': fname,
            'datas': base64.encodebytes(
                etree.tostring(xml).decode().lstrip(BOM_UTF8U).encode('UTF-8') or ''),
            'description': _('XML signed from Invoice %s.') % self.name,
            'res_model': self._name,
            'res_id': self.id,
        }
        self.l10n_mx_edi_cfdi_name = fname
        attachment = self.env['ir.attachment'].create(data_attach)
        # changed
        self.env['l10n_mx_edi.document'].create({
            # 'edi_format_id': self.env.ref('l10n_mx_edi.edi_cfdi_3_3').id,
            'move_id': self.id,
            'state': 'invoice_sent',
            'attachment_id': attachment.id,
            'datetime': fields.Datetime.now(),
            'invoice_ids':[(6, 0, self.ids)]

        })
        self.message_post(attachment_ids=attachment.ids)
        return attachment

    def create_adjustment_line(self, xml_amount):
        """If the invoice has difference with the total in the CFDI is
        generated a new line with that adjustment if is found the account to
        assign in this lines. The account is assigned in a system parameter
        called 'adjustment_line_account_MX'"""
        account_id = self.env['ir.config_parameter'].sudo().get_param(
            'adjustment_line_account_MX', '')
        if not account_id:
            return False
        self.invoice_line_ids.create({
            'account_id': account_id,
            'name': _('Adjustment line'),
            'quantity': 1,
            'price_unit': xml_amount - self.amount_total,
            'invoice_id': self.id,
        })
        return True

    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.company.id)
        domain = [
            ('type', 'in', [TYPE2JOURNAL[ty] for ty in inv_types if ty in TYPE2JOURNAL]),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    @api.model
    def l10n_mx_edi_get_tfd_etree(self, cfdi):
        '''Get the TimbreFiscalDigital node from the cfdi.

        :param cfdi: The cfdi as etree
        :return: the TimbreFiscalDigital node
        '''
        if not hasattr(cfdi, 'Complemento'):
            return None
        attribute = 'tfd:TimbreFiscalDigital[1]'
        namespace = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
        for Complemento in cfdi.Complemento:
            node = Complemento.xpath(attribute, namespaces=namespace)
            if node:
                break
        return node[0] if node else None

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _default_account(self):
        if self._context.get('custom_journal_id'):
            journal = self.env['account.journal'].browse(self._context.get('custom_journal_id'))
            return journal.default_account_id
        return False

    @api.depends('display_type', 'company_id')
    def _compute_account_id(self):
        """
            Author: udit@setuconsulting
            Date: 22/06/23
            Task: Accounting - Vendor Bills - Issue
            Purpose: set account id as set in wizard if invoice is created from attachment
        """
        if self.move_id.filtered(lambda check: check.move_from_attachment):
            accounts_to_assign = {}
            for move_line in self:
                if move_line and move_line.account_id:
                    accounts_to_assign.update({move_line.id: move_line.account_id})
            super()._compute_account_id()
            if accounts_to_assign:
                for move_line in self:
                    move_line.account_id = accounts_to_assign.get(move_line.id)
        else:
            super()._compute_account_id()
