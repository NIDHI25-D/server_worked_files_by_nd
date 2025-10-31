from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _name = 'preorder.forwarder'

    name = fields.Char(string="Name")
