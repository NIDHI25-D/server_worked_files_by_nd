from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    message = fields.Text('Alert message for not drag and drop opportunity manually')

    @api.model
    def get_values(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: get the value of message in settings.
        """
        res = super(ResConfigSettings, self).get_values()
        res['message'] = self.env['ir.config_parameter'].sudo().get_param('setu_crm_automation.message', default='')
        return res

    def set_values(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: set the value of message in settings to save the record of text field.
        """
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('setu_crm_automation.message', self.message or '')
        return res
