from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    send_mail_to_id = fields.Many2one("res.users", string="Send Mail To:",
                                      config_parameter="marvelfields.send_mail_to_id")