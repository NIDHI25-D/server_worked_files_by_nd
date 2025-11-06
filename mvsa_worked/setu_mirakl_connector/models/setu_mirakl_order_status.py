# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SetuMiraklOrderStatus(models.Model):
    _name = "setu.mirakl.order.status"
    _description = 'Mirakl Order Status'

    name = fields.Char(string="Name")
    status = fields.Char(string="Order Status")