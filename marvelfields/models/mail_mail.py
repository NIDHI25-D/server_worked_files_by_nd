from odoo import models, fields, api


class MailMail(models.Model):
    _inherit = 'mail.mail'

    def create(self, values_list):
        """
            Author: jay.garach@setuconsulting.com
            Date: 02/01/25
            Task: Migration from V16 to V18 (https://app.clickup.com/t/86dr27gbh)
            Purpose: set an email_cc as per the purchase order email_cc
        """
        res = super(MailMail, self).create(values_list)
        if res.model == 'purchase.order':
            res.email_cc = self.env['purchase.order'].browse(res.res_id).email_cc
        return res
