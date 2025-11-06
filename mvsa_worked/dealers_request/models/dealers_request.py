from odoo import fields, models, api, _
from datetime import timedelta
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger("dealer_rejected_mails")


class DealerRequest(models.Model):
    _name = "dealer.request"
    _description = 'Dealer Request'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread']

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete="cascade")
    refer = fields.Char(string="Dealer Reference", readonly=True, required=True, copy=False, default='New')
    documents_ids = fields.One2many('documents.document', 'dealer_id', string="Documents")
    status = fields.Selection([('new', 'New'),
                               ('in_process_of_validation', 'In process of Validation '),
                               ('document_upload', 'Document Upload'),
                               ('completed', 'In authorization process'),
                               ('rejected', 'Rejected documents'),
                               ('cancelled', 'Cancelled')],
                               default='new', string="Status")# compute="_compute_dealer_status")
    door = fields.Char(string="Door")
    house = fields.Integer(string="House")
    municipality = fields.Text(string="Municipality")
    credit_limit_requested_id = fields.Many2one("credit.limit.requested", string="Credit Limit Requested")
    credit_limit_assigned = fields.Monetary(string="Credit Limit assigned", default=0.0)
    credit_days_requested_id = fields.Many2one("credit.days.requested", string="Credit days Requested")
    credit_days_assigned_id = fields.Many2one("credit.days.assigned", string="Credit days Assigned")
    elite = fields.Boolean(string="Elite")
    is_dealer_fields_modification_applied = fields.Boolean(compute="compute_is_dealer_fields_modification_applied", default=False)
    is_credit_upload_documents_applied = fields.Boolean(compute="compute_is_dealer_fields_modification_applied",
                                                           default=False)
    def compute_is_dealer_fields_modification_applied(self):
        for line in self:
            line.is_dealer_fields_modification_applied = self.env.user.has_group('dealers_request.dealer_fields_modification')
            line.is_credit_upload_documents_applied = self.env.user.has_group(
                'dealers_request.credit_upload_documents')

    @api.model_create_multi
    def create(self, vals_list):
        """
            Authour: nidhi@setconsulting
            Date: 1/5/2025
            Task: Enhancement to  Registration of clients in the portal { https://app.clickup.com/t/863fv4067 }
            Purpose: This method is used to create Dealer Request
        """
        for vals in vals_list:
            if vals.get('refer', 'New') == 'New':
                vals['refer'] = self.env['ir.sequence'].next_by_code(
                    'dealer.request') or 'New'
        return super(DealerRequest, self).create(vals_list)

    def action_see_documents(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('documents.document_action')
        action['domain'] = [('partner_id', '=', self.partner_id.id), ('folder_id', '=', self.env.ref(
            'dealers_request.documents_dealer_folder', raise_if_not_found=False).id)]
        # action['domain'] = [
        #     '|',
        #     ('type', '=', 'folder'),
        #     '&',
        #     ('res_model', '=', self._name),
        #     ('res_id', '=', self.id),
        # ]
        action['context'] = {
            'default_res_id': self.id,
            'default_res_model': self._name,
            'searchpanel_default_folder_id':  self.env.ref('dealers_request.documents_dealer_folder', raise_if_not_found=False).id,
            # 'searchpanel_default_tag_ids': dealer_tags.ids,
        }
        return action

    def action_reject_docs(self):
        """
            Authour: nidhi@setconsulting
            Date: 1/5/2025
            Task: Enhancement to  Registration of clients in the portal { https://app.clickup.com/t/863fv4067 }
            Purpose: This method is used to send direct mails, when any of the document is rejected from the documents
            Mail Template : Reject Information
        """
        website = self.env['website'].search([], limit=1)
        template_id = self.env.ref('dealers_request.email_template_for_dealer_reject_docs')
        try:
            if self.status == 'rejected' and template_id:
                template_id.send_mail(res_id=self.partner_id.id, force_send=True,
                                      email_values={'recipient_ids': [self.partner_id.id],
                                                    'email_from': website.company_id.email,
                                                    })
                _logger.info("Mail Sent To The Partner : %s " % (self.partner_id.id))
        except Exception as e:
            _logger.info("Issue In Mail Configuration :  %s" % (e))

    def action_completed_docs(self):
        """
            Authour: nidhi@setconsulting
            Date: 1/5/2025
            Task: Enhancement to  Registration of clients in the portal { https://app.clickup.com/t/863fv4067 }
            Purpose: This method is used to send direct mails, when any of the document is completed from the documents
            Mail Template : Dealer request approved
        """
        website = self.env['website'].search([], limit=1)
        template_id = self.env.ref('dealers_request.email_template_for_dealer_completed_docs')
        try:
            if self.status == 'completed' and template_id:
                template_id.send_mail(res_id=self.partner_id.id, force_send=True,
                                      email_values={'recipient_ids': [self.partner_id.id],
                                                    'email_from': website.company_id.email,
                                                    })
                _logger.info("Mail Sent To The Partner : %s " % (self.partner_id.id))
        except Exception as e:
            _logger.info("Issue In Mail Configuration :  %s" % (e))

    @api.constrains('active','inactive')
    def _check_dealer_request(self):
        for request in self:
            if not request.env.user.has_group('dealers_request.credit_upload_documents'):
                raise ValidationError(_("You have no rights to access the records"))

    def unlink(self):
        """
            Authour: nidhi@setconsulting
            Date: 1/5/2025
            Task: Error when send Dealer request images in website. { https://app.clickup.com/t/86drtxjn0 }
            Purpose: delete only those documents in which is_credit_dealer or is_cash_dealer is set of documents.document model
            Branch: error_when_send_dealer_request_images_in_website_mvsa
        """
        documents_to_delete = self.documents_ids.filtered(lambda doc: doc.is_credit_dealer or doc.is_cash_dealer)
        documents_to_delete.unlink()
        return super(DealerRequest, self).unlink()