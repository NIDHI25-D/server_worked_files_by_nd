from odoo import models,fields,api
from odoo.osv import expression

class Website(models.Model):
    _inherit = 'res.company'

    credit_registration_doc = fields.Binary(string="Credit Registration Document",copy=False)
    credit_registration_doc_name = fields.Char('File Name')

    credit_request_doc = fields.Binary(string="Credit Request Document", copy=False)
    credit_request_doc_name = fields.Char('File Name')

    promissary_note_doc = fields.Binary(string="Promissary Note Document", copy=False)
    promissary_note_doc_name = fields.Char('File Name')

    # ------------------Fields for help documents---------------------------------------
    credit_registration_doc_help = fields.Binary(string="Credit Registration Document Help Document", copy=False)
    credit_registration_doc_name_help = fields.Char('File Name')

    credit_request_doc_help = fields.Binary(string="Credit Request Document Help Document", copy=False)
    credit_request_doc_name_help = fields.Char('File Name')

    promissary_note_doc_help = fields.Binary(string="Promissary note Document Help Document", copy=False)
    promissary_note_doc_name_help = fields.Char('File Name')

    # ------------------Fields for Address------TASK : Enhancements to the Dealer Request process. Phase 1.--------------
    credit_general_address = fields.Html(string="Credit Address",
                                         help="Add the address which will be seen after credit customers add the documents")