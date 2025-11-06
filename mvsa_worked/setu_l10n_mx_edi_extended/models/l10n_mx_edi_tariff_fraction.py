# coding: utf-8

from odoo import fields, models, api


class L10nMXEdiTariffFraction(models.Model):
    _inherit = 'l10n_mx_edi.tariff.fraction'

    igi = fields.Float(string="IGI")
    iva = fields.Float(string="IVA")
