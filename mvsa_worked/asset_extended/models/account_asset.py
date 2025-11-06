from odoo import fields, models, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    brand = fields.Char(string='Brand')
    model = fields.Char(string='Model')
    serial_number = fields.Char(string='Serial Number')
    warranty = fields.Boolean(string="Warranty")
    warranty_period = fields.Date(string='Warranty period')
    status = fields.Selection(
        [("active", "Active In Use"), ("current", "Current Assets"), ("obsolete", "Obsolete"), ("to_find", "To Find")],
        string='Asset Status')
    employee_id = fields.Many2one('hr.employee')
    subcategories_ids = fields.One2many('asset.subcategories', 'asset_id',
                                        string="Subcategories")
    is_responsive_letter = fields.Boolean(string="Responsive Letter")
    comments = fields.Text(string="Comments")
