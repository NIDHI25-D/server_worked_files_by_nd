from odoo import api, fields, models


class ServerActions(models.Model):
    _inherit = 'ir.actions.server'

    activity_user_type = fields.Selection(selection_add=[('sevrals_users', 'Several Users')])
    activity_sevral_users_ids = fields.Many2many('res.users', string="Multiple Responsible")
