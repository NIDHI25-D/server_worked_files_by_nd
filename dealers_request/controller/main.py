from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64
from odoo.exceptions import ValidationError

class CustomerPortal(CustomerPortal):

    def create_attachment_doc(self, data, doc):
        file = data
        if file.filename.split(".")[-1] in ['png', 'jpg', 'jpeg','pdf']:
            attachment_value = {
                'name': file.filename,
                'datas': base64.encodebytes(file.read()),
                'res_model': 'documents.document',
                'res_id': doc.id,
            }
            attachment = request.env['ir.attachment'].sudo().create(attachment_value)
            return attachment
        else :
            raise ValidationError(_("Please Upload pdf/png/jpg.jpeg documents"))

    @http.route(['/my/dealer'], type='http', auth='user', website=True)
    def dealer_request_file(self, **kw):
        partner_id = request.env.user.sudo().partner_id
        dealer_document_id = request.env.ref('dealers_request.documents_dealer_folder').id
        dealer_partner = request.env['dealer.request'].sudo().search([('partner_id', '=', partner_id.id)])
        # folder = request.env['documents.folder'].sudo().search([('id', '=', dealer_document_id)])

        document = request.env['documents.document'].sudo().search(
            [('partner_id', '=', partner_id.id),
            ('folder_id', '=', dealer_document_id)])
        to_approve = request.env.ref('dealers_request.documents_dealer_status_to_validate').id
        validate = request.env.ref('dealers_request.documents_dealer_status_validate').id
        reject = request.env.ref('dealers_request.documents_dealer_status_reject').id

        un_approved = document.filtered(lambda x: x.tag_ids.id in (to_approve, reject))
        website_not_approved = document.filtered(lambda x: x.tag_ids.id == to_approve)
        rejected_doc = document.filtered(lambda x: x.tag_ids.id == reject)
        is_cash_dealer_send = {'proof_of_address': _('Proof of Address'),
                               'proof_of_tax_situation': _('Proof of Tax Situation'),
                               'ine_front': _('INE (Front)'),
                               'ine_reverse': _('INE (Reverse)'),
                               'business_photography_outdoor': _('Business Photography (Outdoor)'),
                               'business_photography_indoor_1': _('Business Photography (Indoor 1)'),
                               'business_photography_indoor_2': _('Business Photography (Indoor 2)'),
                               }
        is_credit_dealer_send = is_cash_dealer_send.copy()
        is_credit_dealer_send.update({
                                 'formato_d_32': _('Formato D32 ( opinnion Positiva )'),
                                 'credit_registration': _('Credit Registration'),
                                 'credit_request': _('Credit Request'),
                                 'power_of_attorney': _('Power Of Attorney'),
                                 'constitutive_act': _('Constitutive Act'),
                                 'promissary_note': _('Promissary note'),
                                 'aval_ine_front': _('Aval INE ( Front )'),
                                 'aval_ine_reverse': _('Aval INE ( Reverse )'),
                                 'aval_proof_of_address': _('Aval Proof Of Address'),
                                 'balance_sheet': _('Balance Sheet'),
                                 'income_statements': _('Income Statements'),
                                 })
        approved_doc = un_approved.mapped(dealer_partner.dealer_type)
        credit_limit_requested_value = request.env['credit.limit.requested'].sudo().search([('id', '=', kw.get('credit_limit_requested'))])
        credit_days_requested_value = request.env['credit.days.requested'].sudo().search([('id', '=', kw.get('credit_days_requested'))])
        doc_send_cash_dealer = {k:v for k,v in is_cash_dealer_send.items() if k in approved_doc }
        doc_send_credit_dealer = {k: v for k, v in is_credit_dealer_send.items() if k in approved_doc}
        values = {
                'dealer_partner': dealer_partner,
                'partner_id': partner_id,
                'is_cash_dealer': [doc_send_cash_dealer if doc_send_cash_dealer else is_cash_dealer_send],
                'is_credit_dealer': [doc_send_credit_dealer if doc_send_credit_dealer else is_credit_dealer_send],
                'reject_reason':rejected_doc,
                'company' : request.env.company,
            }

        if kw:
            kw_without_null = {x: y for x, y in kw.items() if (y is not '')}
            if kw.get('is_cash_dealer'):
                kw_without_null.pop('is_cash_dealer')
            if kw.get('is_credit_dealer'):
                kw_without_null.pop('is_credit_dealer')
                if kw.get('credit_days_requested'):
                    kw_without_null.pop('credit_days_requested')
                if kw.get('credit_limit_requested'):
                    kw_without_null.pop('credit_limit_requested')
            selected_file_attachment = []
            if kw.get('is_cash_dealer'):
                attachment_list = ['proof_of_address', 'proof_of_tax_situation', 'ine_front', 'ine_reverse',
                                   'business_photography_outdoor', 'business_photography_indoor_1',
                                   'business_photography_indoor_2']
            if kw.get('is_credit_dealer'):
                attachment_list = ['proof_of_address', 'proof_of_tax_situation', 'ine_front', 'ine_reverse',
                                   'formato_d_32', 'credit_registration', 'credit_request', 'power_of_attorney',
                                   'constitutive_act', 'promissary_note', 'aval_ine_front', 'aval_ine_reverse',
                                   'aval_proof_of_address', 'balance_sheet', 'income_statements',
                                   'business_photography_outdoor'
                                   'business_photography_indoor_1', 'business_photography_indoor_2']
            if dealer_partner:
                dealer_partner.sudo().action_see_documents()
            else:
                dealer_request = request.env['dealer.request'].sudo().create(
                    {
                        'dealer_type': list(kw.keys())[0],
                        'name': partner_id.name,
                        'partner_id': partner_id.id,
                        'credit_limit_requested_id' : credit_limit_requested_value.id,
                        'credit_days_requested_id': credit_days_requested_value.id,
                    }
                )
            if not un_approved:
                for create_document in kw_without_null:
                    if kw.get(create_document).filename:
                        file_obj = kw.get(create_document) #added
                        attachment = self.create_attachment_doc(file_obj, dealer_request) #added
                        document = request.env['documents.document'].sudo().create({
                            'name':file_obj.filename,
                            'attachment_id': attachment.id, #added
                            # 'name': kw.get(create_document).filename,
                            'dealer_id': dealer_request.id,
                            'owner_id': request.env.user.sudo().id,
                            'partner_id': request.env.user.sudo().partner_id.id,
                            'res_model': 'dealer.request',
                            'folder_id': request.env.ref('dealers_request.documents_dealer_folder').id,
                            'res_id': dealer_request.id,
                            'tag_ids': request.env.ref('dealers_request.documents_dealer_status_to_validate'),
                        })
                        document.update({list(kw.keys())[0]: create_document})
                        # attachment = self.create_attachment_doc(kw.get(create_document), document)
                        selected_file_attachment.append(attachment.id)
                        # Chatter for submitted documents
                        request.env['mail.message'].sudo().create({
                            'model': 'dealer.request',
                            'res_id': dealer_request.id,
                            'attachment_ids': [(6, 0, attachment.ids)],
                            'subject': 'Documents',
                        })
            else:
                for doc in un_approved:
                    doc.attachment_id = self.create_attachment_doc(kw[doc[dealer_partner.dealer_type]], doc).id
                    doc.update({'tag_ids': request.env.ref('dealers_request.documents_dealer_status_to_validate')})
                    # Chatter for rejected documents
                    request.env['mail.message'].sudo().create({
                        'model': 'dealer.request',
                        'res_id': dealer_partner.id,
                        'attachment_ids': [(6, 0, doc.attachment_id.ids)],
                        'subject': 'Submission of Rejected Documents',
                    })
            for record in kw_without_null:
                if record in attachment_list:
                    print(record)
            return request.render("dealers_request.dealer_form_submit", values)
        if dealer_partner.status == 'completed':
            return request.render("dealers_request.dealer_form_approved_page", values)
        if dealer_partner.status == 'rejected' and  dealer_partner.status != 'in_process_of_validation' and dealer_partner.status != 'completed' and website_not_approved:
            return request.render("dealers_request.dealer_form_submit", values)
        if dealer_partner.status != 'rejected' and  dealer_partner.status == 'in_process_of_validation' and dealer_partner.status != 'completed' and website_not_approved:
            return request.render("dealers_request.dealer_form_submit", values)
        if dealer_partner.status == 'new' and dealer_partner.status != 'in_process_of_validation' and dealer_partner.status != 'completed' and website_not_approved:
            return request.render("dealers_request.dealer_form_submit", values)
        return request.render("dealers_request.dealer_request_type", values)
