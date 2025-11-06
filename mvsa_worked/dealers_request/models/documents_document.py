from odoo import fields, models, api, _
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger("dealer_rejected_mails")


class Document(models.Model):
    _inherit = "documents.document"

    dealer_id = fields.Many2one("dealer.request", string="Dealer")
    proof_of_address_doc_id = fields.Many2one("dealer.request", string="proof_of_address")
    is_cash_dealer = fields.Selection([
        ('proof_of_address', 'Proof of address'),
        ('proof_of_tax_situation', 'Proof of Tax Situation'),
        ('ine_front', 'INE (Front)'),
        ('ine_reverse', 'INE (Reverse)'),
        ('business_photography_outdoor', 'Business Photography (Outdoor)'),
        ('business_photography_indoor_1', 'Business Photography (Indoor 1)'),
        ('business_photography_indoor_2', 'Business Photography (Indoor 2)')], string="Cash Dealer")

    is_credit_dealer = fields.Selection([
        ('proof_of_address', 'Proof of address'),
        ('proof_of_tax_situation', 'Proof of Tax Situation'),
        ('ine_front', 'INE (Front)'),
        ('ine_reverse', 'INE (Reverse)'),
        ('formato_d_32', 'Formato D32 ( opinnion Positiva )'),
        ('credit_registration', 'Credit Registration'),
        ('credit_request', 'Credit Request'),
        ('power_of_attorney', 'Power Of Attorney'),
        ('constitutive_act', 'Constitutive Act'),
        ('promissary_note', 'Promissary note'),
        ('aval_ine_front', 'Aval INE ( Front )'),
        ('aval_ine_reverse', 'Aval INE ( Reverse )'),
        ('aval_proof_of_address', 'Aval Proof Of Address'),
        ('balance_sheet', 'Balance Sheet'),
        ('income_statements', 'Income Statements'),
        ('business_photography_outdoor', 'Business Photography (Outdoor)'),
        ('business_photography_indoor_1', 'Business Photography (Indoor 1)'),
        ('business_photography_indoor_2', 'Business Photography (Indoor 2)'),
    ], string="Credit Dealer")
    reject_reason = fields.Many2one("reject.reason", string="Reject Reason")

    def write(self, vals):
        res = super(Document, self).write(vals)
        reject = self.env.ref('dealers_request.documents_dealer_status_reject')
        to_approve = self.env.ref('dealers_request.documents_dealer_status_to_validate')
        validate = self.env.ref('dealers_request.documents_dealer_status_validate')
        if self.dealer_id :
            if (vals.get('tag_ids') and vals.get('tag_ids')[0][2] == to_approve.ids
                    and self.dealer_id.documents_ids.mapped('tag_ids') == validate + to_approve):
                self.dealer_id.status = 'in_process_of_validation'

            elif (vals.get('tag_ids') and vals.get('tag_ids')[0][2] == validate.ids
                  and self.dealer_id.documents_ids.mapped('tag_ids') != to_approve + reject
                  and self.dealer_id.documents_ids.mapped(
                        'tag_ids') != to_approve + validate and self.dealer_id.status != 'rejected'
                  and self.dealer_id.status != 'completed'):
                self.dealer_id.status = 'completed'
                self.dealer_id.action_completed_docs()

            elif (vals.get('tag_ids') and vals.get('tag_ids')[0][2] == validate.ids
                  and self.dealer_id.documents_ids.mapped('tag_ids') == to_approve + validate):
                self.dealer_id.status = 'in_process_of_validation'

            elif (vals.get('tag_ids') and vals.get('tag_ids')[0][2] == to_approve.ids):
                self.dealer_id.status = 'in_process_of_validation'
    
            elif (vals.get('tag_ids') and vals.get('tag_ids')[0][2] == reject.ids
                  and self.dealer_id.status != 'rejected'):
                self.dealer_id.status = 'rejected'
                self.dealer_id.action_reject_docs()
        return res
