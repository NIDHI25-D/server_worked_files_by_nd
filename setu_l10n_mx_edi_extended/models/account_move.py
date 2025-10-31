from odoo import fields, models, api

import logging

_logger = logging.getLogger(__name__)


class AccountMoveExtended(models.Model):
    _inherit = "account.move"

    l10n_mx_edi_cfdi_name = fields.Char(string='CFDI name', copy=False, readonly=True,
                                        help='The attachment name of the CFDI.')



    # commented this because no need anymore here currently.
    # @api.model
    # def l10n_mx_edi_get_tfd_etree(self, cfdi):
    #     """Get the TimbreFiscalDigital node from the cfdi."""
    #     if not hasattr(cfdi, 'Complemento'):
    #         return None
    #     attribute = 'tfd:TimbreFiscalDigital[1]'
    #     namespace = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
    #     node = cfdi.Complemento.xpath(attribute, namespaces=namespace)
    #     return node[0] if node else None
    #
    # @api.model
    # def l10n_mx_edi_get_xml_etree(self, cfdi=None):
    #     '''Get an objectified tree representing the cfdi.
    #     If the cfdi is not specified, retrieve it from the attachment.
    #
    #     :param cfdi: The cfdi as string
    #     :return: An objectified tree
    #     '''
    #
    #     self.ensure_one()
    #     if cfdi is None and self.l10n_mx_edi_cfdi:
    #         cfdi = self.l10n_mx_edi_cfdi
    #     return fromstring(cfdi) if cfdi else None
