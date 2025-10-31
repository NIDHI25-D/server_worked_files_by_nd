from odoo import api, fields, models

class PortalWizardUser(models.TransientModel):
    
    _inherit = 'portal.wizard.user'
    
    def action_grant_access(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 21/03/25
            Task: Migration to v18 from v16
            Purpose: is company user is True if conditions are fulfilled from the server action Grant portal access.
        """
        if self.partner_id.name and self.partner_id.street and self.partner_id.email and self.partner_id.country_id and self.partner_id.vat and not self.partner_id.is_company_user:
            self.partner_id.is_company_user = True
        return super(PortalWizardUser,self).action_grant_access()