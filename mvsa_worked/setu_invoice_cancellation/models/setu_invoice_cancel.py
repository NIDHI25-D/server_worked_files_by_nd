# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SetuInvoiceCancel(models.Model):
    _name = 'setu.invoice.cancel'
    _description = 'Setu Invoice Cancel'

    name = fields.Char()
    is_return = fields.Boolean()
