from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # price_list_id_for_customer = fields.Many2one('product.pricelist', string="Price List")
    message_for_customer_in_monthly_proposal = fields.Text('Alert message for not drag and drop opportunity manually')
    # interval = fields.Integer(string="Interval", default=365)
    # products_to_load = fields.Integer(string="Products To Load")
    monthly_proposal_mail_user = fields.Many2one('res.users','Monthly proposal mail user')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        message_for_customer_in_monthly_proposal = IrDefault._get('res.config.settings',
                                                                 'message_for_customer_in_monthly_proposal',
                                                                 company_id=self.env.company.id)
        monthly_proposal_mail_user = IrDefault._get('res.config.settings', 'monthly_proposal_mail_user',
                                company_id=self.env.company.id)
        res.update(monthly_proposal_mail_user=monthly_proposal_mail_user)
        res.update(message_for_customer_in_monthly_proposal=message_for_customer_in_monthly_proposal)
        return res

    @api.model
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', 'message_for_customer_in_monthly_proposal',
                      self.message_for_customer_in_monthly_proposal or '',
                      company_id=self.env.company.id)
        IrDefault.set('res.config.settings', 'monthly_proposal_mail_user',
                      self.monthly_proposal_mail_user.id or False,
                      company_id=self.env.company.id)
        return res
