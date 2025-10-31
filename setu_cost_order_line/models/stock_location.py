from odoo import fields, models, api


class StockLocation(models.Model):
    _inherit = "stock.location"

    return_location = fields.Boolean(string='Is a return location', copy=False, help='Check this box to allow using this location as a return location.')
