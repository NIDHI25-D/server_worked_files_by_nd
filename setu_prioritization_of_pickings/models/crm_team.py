from odoo import fields, models, api


class SalesTeam(models.Model):
    _inherit = 'crm.team'

    is_ecommerce_team = fields.Boolean(string="Ecommerce Related ?")
