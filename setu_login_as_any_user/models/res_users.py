from odoo import api, fields, models
import uuid


class ResUsers(models.Model):
    _inherit = 'res.users'

    temp_auth_token = fields.Char('Auth Token')
    token_limit = fields.Datetime()

# df85c263ab8fe5e768d77f0f5dfef2cde3c68713