from odoo.http import request
from odoo import http, SUPERUSER_ID, _
import base64

from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    def create_attachment_sale_order(self, data,model, order):
        file = data
        if file.filename.split(".")[-1] in ['png', 'jpg', 'jpeg'] or ['mp4', 'mkv', 'webm'] or ['pdf', 'docx', 'txt']:
            attachment_value = {
                'name': file.filename,
                'datas': base64.encodebytes(file.read()),
                'res_model': model,
                'res_id': order,
            }
            attachment = request.env['ir.attachment'].sudo().create(attachment_value)
            return attachment

    @http.route(['/my/attach_payment_receipt/submit'], type='http', auth='user', website=True, method=['POST'])
    def attach_payment_receipt(self, **kw):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/02/2025
            Task: Payment voucher planification activity automate.
            Purpose: There are two configurations in the settings. One is related to the words of comment and other is related to the pricelist.
            -->Now when the user adds comment in done sale order, then their words will be matched with the words mentioned in the settings field.
               if the words as well as pricelist are matched, then it will create a schedule activity respectively.
            -->In Schedule activity user is to assigned as Sale_order's -> partner_id's -> Collection Executive.
               Now if this is not assigned, then there will be message_post regarding the users and activity will not be created.
            -->If neither price-list nor words are matched as per the setting configuration than respected sale order will have a message_post.

            --> This methods also includes voucher of Invoice send from the website of Pay now Invoice
        """
        if kw.get('payment_voucher'):
            file = kw.get('payment_voucher')
            order = int(kw.get('order'))
            model = 'sale.order'
            if file:
                attachment = self.create_attachment_sale_order(file,model, order)
                website = request.env['website'].get_current_website()
                sale_order = request.env['sale.order'].sudo().browse(order)
                user_assign = sale_order.partner_id.collection_executive_id
                mode_sale_id = request.env['ir.model'].search([('model', '=', 'sale.order')])
                request.env['mail.message'].sudo().create({
                    'subject': 'Payment Voucher Receipt',
                    'model': 'sale.order',
                    'res_id': order,
                    'attachment_ids': [(6, 0, attachment.ids)],
                })
                if user_assign and sale_order.pricelist_id.send_mail_activity:
                    request.env['mail.activity'].sudo().create({
                        'activity_type_id': request.env.ref('mail.mail_activity_data_todo').id,
                        'res_id': order,
                        'res_model_id': mode_sale_id.id,
                        'user_id': user_assign.id,
                        'summary': sale_order.pricelist_id.send_mail_activity_msg,
                    })
                else:
                    sale_order.sudo().message_post(
                        body=_("Contact : %s have not assigned Collection Executive.So kindly add Collection Executive",
                               sale_order.partner_id.name))
                so_url = '/my/orders/%s?%s' % (order, sale_order.access_token)
                if attachment:
                    sale_order.is_sent_payment_receipt = True
                return request.redirect(so_url)

        if kw.get('payment_voucher_invoice'):
            file = kw.get('payment_voucher_invoice')
            order = int(kw.get('invoice_order'))
            model = 'account.move'
            if file:
                attachment = self.create_attachment_sale_order(file,model, order)
                website = request.env['website'].get_current_website()
                account_move = request.env[model].sudo().browse(order)
                user_assign = account_move.partner_id.collection_executive_id
                mode_account_id = request.env['ir.model'].search([('model', '=', model)])
                request.env['mail.message'].sudo().create({
                    'subject': 'Payment Voucher Receipt for Invoice',
                    'model': model,
                    'res_id': order,
                    'attachment_ids': [(6, 0, attachment.ids)],
                })
                if user_assign :
                    request.env['mail.activity'].sudo().create({
                        'activity_type_id': request.env.ref('mail.mail_activity_data_todo').id,
                        'res_id': order,
                        'res_model_id': mode_account_id.id,
                        'user_id': user_assign.id,
                        'summary': _(f"Validate Payment"),
                    })
                else:
                    account_move.sudo().message_post(
                        body=_("Contact : %s have not assigned Collection Executive.So kindly add Collection Executive",
                               account_move.partner_id.name))
                ac_url = '/my/invoices/%s?access_token=%s' % (order, account_move.access_token)
                if attachment:
                    account_move.is_sent_payment_receipt_account = True
                return request.redirect(ac_url)


