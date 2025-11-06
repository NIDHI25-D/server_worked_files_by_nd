import uuid
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection([('natural', 'Natural'), ('legal', 'Legal Entity')],
                                    string='Partner_type', required=False)
    is_verified_partner = fields.Boolean(string='Verified Partner', default=0)
    verification_token = fields.Char(readonly=True)

    @api.model
    def simple_vat_check(self, country_code, vat_number):
        """
            Author: jay.garach@setuconsulting.com
            Date: 19/03/25
            Task: Migration from V16 to V18
            Purpose: To first check partner's country code matched with its vat-first 2 digit or not? and also check
                     if check_vat_{country_code} function exists or not?
        """
        if self.country_id.code:
            check_func_name = 'check_vat_' + self.country_id.code.lower()
            if self.country_id and self.country_id.code.lower() != country_code.lower() and not getattr(self,
                                                                                                        check_func_name,
                                                                                                        None):
                return False
        return super(ResPartner, self).simple_vat_check(country_code=country_code, vat_number=vat_number)
