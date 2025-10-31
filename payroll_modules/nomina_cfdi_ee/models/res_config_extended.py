from odoo import fields, models, api


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    automatic_vacation_id = fields.Many2one(comodel_name='hr.leave.type', string='Use for automatic vacation allocation'
                                            , config_parameter='nomina_cfdi_ee.automatic_vacation_id')
