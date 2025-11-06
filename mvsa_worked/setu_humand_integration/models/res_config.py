from odoo import models, fields, api


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    days_to_get_time_off_requests = fields.Integer(string="Time-Off Requests Days",
                                                   config_parameter='setu_humand_integration.days_to_get_time_off_requests')
