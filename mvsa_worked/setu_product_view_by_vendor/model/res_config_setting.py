from odoo import fields, models,api
from ast import literal_eval


class ResConfigSetting(models.TransientModel):

    _inherit = 'res.config.settings'

    mail_to = fields.Many2many('res.users',string="Email")
    interval_time_to_send_mail = fields.Integer(string="Interval time in minutes", default=20,config_parameter="setu_product_view_by_vendor.interval_time_to_send_mail")

    @api.model
    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        icp_sudo_vendor = self.env['ir.config_parameter'].sudo()
        mail_to = icp_sudo_vendor.get_param('setu_product_view_by_vendor.mail_to')

        res.update(
            mail_to=[
                (6, 0, literal_eval(mail_to))] if mail_to else False,
        )
        return res

    def set_values(self):
        res = super(ResConfigSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'setu_product_view_by_vendor.mail_to',
            self.mail_to.ids)
        return res
