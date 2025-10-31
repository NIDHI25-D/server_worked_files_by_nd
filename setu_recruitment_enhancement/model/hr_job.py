from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class HrJob(models.Model):
    _inherit = "hr.job"

    open_date = fields.Datetime(string="Open Date", copy=False)
    close_date = fields.Datetime(string="Close Date", compute="_compute_close_date", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        self.env.registry.clear_cache()
        return super(HrJob, self).create(vals_list)

    def write(self, vals):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/01/25
            Task: Migration from V16 to V18
            Purpose: This method is used to write for hr.job, when all the employees are fulfilled as per the required
                   candidates, then it will give validation error respectively if the user enables the toggle button.
        """
        self.env.registry.clear_cache()
        res = super(HrJob, self).write(vals)
        publish = vals.get('is_published')
        if publish:
            if not self.open_date:
                for record in self:
                    if record.is_published:
                        record.open_date = datetime.now()
            else:
                if self.close_date:
                    raise ValidationError(_("Job you are trying to post has been fulfilled, please create a new one."))
        return res

    @api.depends('application_ids.stage_id')
    def _compute_close_date(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/01/25
            Task: Migration from V16 to V18
            Purpose: This method will give close date with the conditions that when the last applicant assigned in the
                    status : contract signed that date will be assigned in the field of close date and is_published toggle
                    will be close and a message in chatter will be added.
        """
        _logger.debug("Compute _compute_close_date method start")
        for record in self:
            contract_signed_stage_id = self.env.ref('hr_recruitment.stage_job5').id
            contract_signed_applicants = record.application_ids.search(
                [('job_id', '=', record.id), ('stage_id', '=', contract_signed_stage_id), ('date_closed', '>=', record.open_date)])
            if contract_signed_applicants and record.no_of_recruitment == len(contract_signed_applicants) and \
                    not record.close_date:
                record.close_date = datetime.now()
                record.is_published = False
                record.message_post(
                    body=_("Expected Employees '%d' are fulfilled") % (
                        record.no_of_recruitment))
        _logger.debug("Compute _compute_close_date method end")
