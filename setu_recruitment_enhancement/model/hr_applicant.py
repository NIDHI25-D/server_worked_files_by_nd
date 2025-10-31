from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    @api.model_create_multi
    def create(self, vals_list):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/01/25
            Task: Migration from V16 to V18
            Purpose:This method will create an applicant with conditions that contract_signed member matches the count of required
                 employee then it will show respected Validation error while creation of applicant
        """
        self.env.registry.clear_cache()
        res = super(HrApplicant, self).create(vals_list)
        contract_signed_stage_id = self.env.ref('hr_recruitment.stage_job5').id
        for vals in vals_list:
            if vals.get('stage_id') and vals.get('stage_id') == contract_signed_stage_id:
                for record in res:
                    if record.job_id:
                        contract_signed_applicants = record.search(
                            [('job_id', '=', record.job_id.id), ('stage_id', '=', contract_signed_stage_id)])
                        if contract_signed_applicants and record.job_id.no_of_recruitment < len(contract_signed_applicants):
                            raise ValidationError(_("Requirement for the job is fulfilled"))
            elif vals.get('stage_id'):
                for record in res:
                    if record.job_id and record.job_id.close_date:
                        raise ValidationError(_("Cannot create new applicant as requirement are fulfilled"))
        return res

    def write(self, vals):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/01/25
            Task: Migration from V16 to V18
            Purpose:This method will write an applicant with conditions that if a contract_signed member matches the count
                   of required employee then it will show respected Validation error while creation of applicant
        """
        res = super(HrApplicant, self).write(vals)
        self.env.registry.clear_cache()
        contract_signed_stage_id = self.env.ref('hr_recruitment.stage_job5').id
        if vals.get('stage_id') and vals.get('stage_id') == contract_signed_stage_id:
            for record in self:
                if record.job_id:
                    contract_signed_applicants = record.search(
                        [('job_id', '=', record.job_id.id), ('stage_id', '=', contract_signed_stage_id), ('date_closed', '>=', record.job_id.open_date)])
                    if contract_signed_applicants and record.job_id.no_of_recruitment < len(contract_signed_applicants):
                        raise ValidationError(_("Requirement for the job is fulfilled"))
        elif vals.get('stage_id'):
            for record in self:
                if record.job_id and record.job_id.close_date:
                    raise ValidationError(_("Cannot change the stage as requirement are fulfilled"))
        return res
