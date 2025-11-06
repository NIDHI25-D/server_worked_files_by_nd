from odoo import fields, models


class MeliWarehouse(models.Model):
    _name = 'meli.warehouse'

    # https://app.clickup.com/t/865d9mvqa
    # Done with requirement related to the export multiple location stock to the meli oerp.
    company_id = fields.Many2one('res.company')
    warehouse_id = fields.Many2one('stock.warehouse')
    location_ids = fields.Many2many('stock.location', 'meli_stock_location')
