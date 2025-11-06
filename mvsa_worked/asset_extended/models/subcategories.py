from odoo import fields, models, api


class AssetSubcategories(models.Model):
    _name = "asset.subcategories"
    _description = "Asset subcategories"

    name = fields.Char(string='Name')
    asset_id = fields.Many2one('account.asset', string="Asset")