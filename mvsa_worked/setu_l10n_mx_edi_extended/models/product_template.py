# coding: utf-8

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    igi = fields.Float(related="l10n_mx_edi_tariff_fraction_id.igi", string="IGI", store=True)
    iva = fields.Float(related="l10n_mx_edi_tariff_fraction_id.iva", string="IVA", store=True)