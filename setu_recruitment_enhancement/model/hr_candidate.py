from odoo import api, models, fields




class HrCandidate(models.Model):
    _inherit = "hr.candidate"

    def _inverse_partner_email(self):
        """
            Author: nidhi@setconsulting.com
            Date: 18/09/25
            Task: Create employee issue { https://app.clickup.com/t/86dxefptr}
            Purpose: Because of the ‘Convertir Nombre a Mayúsculas’ automated rule,
                    candidate.partner_id.name is set to uppercase.
                    This causes the condition candidate.partner_id.name == candidate.email_from to evaluate as false,
                    and as a result, candidate.partner_id.name set with the email address.
                    To overcome this issue added changes
                    -- as per meeting 'Convertir Nombre a Mayúsculas' don't want to archive action
         """
        res= super(HrCandidate,self)._inverse_partner_email()
        for candidate in self:
            if candidate.partner_name and (not candidate.partner_id.name or candidate.partner_id.name.lower() == candidate.email_from):
                candidate.partner_id.name = candidate.partner_name
        return res
