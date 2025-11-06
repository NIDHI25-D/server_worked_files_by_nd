from odoo import models, fields


class SetuMultiEcommerceConnector(models.Model):
    _inherit = 'setu.multi.ecommerce.connector'

    is_dem_project = fields.Boolean(string="Is DEM Project")
    dem_partner_id = fields.Many2one('res.partner', string="Customer Name")
    discount_percentage = fields.Float('Set the discount percentage')
