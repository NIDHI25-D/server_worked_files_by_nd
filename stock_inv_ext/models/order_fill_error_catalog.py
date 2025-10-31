from odoo import models, fields, api, _


class OrderFillErrorCatalog(models.Model):
    _name = 'order.fill.error.catalog'
    _description = 'Order Fill Error Catalog'

    name = fields.Char(string="Name")
