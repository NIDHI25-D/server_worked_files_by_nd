from odoo import models, fields, api

# not used this..
# class AccountEdiDocument(models.Model):
#     _inherit = 'account.edi.document'
#
#     def _process_documents_web_services(self, job_count=None, with_commit=True):
#         """
#         Added By : Ravi Kotadiya
#         Added On : Dec-23-2021
#         Use : To use the zip of supplier For Invoice Approval instead of company partner zip only for cron process
#         :param move:
#         :return:
#         """
#         self = self.with_context(is_called_from_cron=True)
#         return super(AccountEdiDocument, self)._process_documents_web_services(job_count=job_count,
#                                                                                with_commit=with_commit)



