import base64
from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class CustomerPortal(CustomerPortal):

    def create_attachment(self, data,claim):
        """
          Author: jay.garach@setuconsulting.com
          Date: 25/03/25
          Task: Migration from V16 to V18
          Purpose: it's creating attachments that are attached to new claim from website
        """
        file = data
        if file.filename.split(".")[-1] in ['png', 'jpg', 'jpeg'] or ['mp4', 'mkv', 'webm'] or ['pdf', 'docx', 'txt']:
            attachment_value = {
                'name': file.filename,
                'datas': base64.encodebytes(file.read()),
                'res_model': "crm.claim",
                'res_id': claim.id,
            }
            attachment = request.env['ir.attachment'].sudo().create(attachment_value)
            return attachment

    @http.route(['/my/claims', '/my/claims/page/<int:page>'], type='http', auth='user', website=True)
    def get_claims(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        """
          Author: jay.garach@setuconsulting.com
          Date: 25/03/25
          Task: Migration from V16 to V18
          Purpose: showing the claims related to user to website.
        """
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        crm_claim = request.env['crm.claim'].sudo()

        domain = [('partner_id', '=', partner.id)]

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {'date': {'label': _('Order Date'), 'claim_order': 'date desc, id desc'}}

        if not sortby:
            sortby = 'date'
        claims = searchbar_sortings[sortby]['claim_order']

        claims_count = crm_claim.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/my/claims",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=claims_count,
            page=page,
            step=self._items_per_page
        )

        claims = crm_claim.search(
            domain,
            order=claims,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        values.update({
            'page_name': 'claim',
            'date': date_begin,
            'claims': claims.sudo(),
            'pager': pager,
            'default_url': '/my/claims',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("setu_claims_from_website.portal_my_orders_of_claims", values)

    @http.route(['/my/claims/create-claim', '/my/claims/create-claim/<int:invoice>'], type='http', auth='user', website=True)
    def create_new_claims(self, invoice=False, **kw):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: managing the new claim request.
        """
        if invoice:
            invoice = request.env['account.move'].sudo().browse(int(invoice))
            if invoice.partner_id.id != request.env.user.partner_id.id and invoice.state not in ['posted']:
                return request.redirect('/my/invoices')
        else:
            invoice = False
        partner = request.env.user.partner_id
        if not partner.invoice_ids:
            return request.redirect('/my')
        values = {
            'page_name': 'create-claim',
            'default_url': 'my/claims/create-claim',
            'partner': partner,
            'partner_invoice': invoice,
        }
        return request.render("setu_claims_from_website.new_claim_form", values)

    @http.route(['/create-claim/submit'], type='http', auth='user', website=True)
    def create_claims(self, **kw):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: while get submitted claim it create the claim with given value in form.
        """
        responsible_id = request.env['account.move'].sudo().browse(int(kw.get('invoice_id'))).team_id.serviceagent_id
        product_id = request.env['product.product'].sudo().browse(int(kw.get('js_model')))
        claim = request.env["crm.claim"].sudo().create({
            'name': request.env['ir.sequence'].sudo().next_by_code('crm.claim') or 'New',
            'ref': kw.get('serial_number'),
            'invoice_ids': [(6, 0, [int(kw.get('invoice_id'))])],
            'partner_id': int(kw.get('partner_id')),
            'contact_information': kw.get('contact_info'),
            'partner_phone': kw.get('partner_phone'),
            'email_from': kw.get('email_from'),
            'team_id': int(kw.get('team_id')),
            'categ_id': int(kw.get('js_claim')),
            'description': kw.get('desc'),
            'product_tmpl_id': int(product_id.product_tmpl_id.id),
            'product_id': int(product_id.id),
            'user_id': int(responsible_id.id)
        })
        selected_file_attachment = []
        attachment_list = ['add_evidence_image', 'add_evidence_image_1', 'add_evidence_image_2', 'add_evidence_video', 'add_evidence_text']
        for data in attachment_list:
            if kw.get(data):
                attachment = self.create_attachment(kw.get(data), claim)
                selected_file_attachment.append(attachment.id)
        claim.message_post(body="The document is successfully uploaded", attachment_ids=selected_file_attachment)

        vals = {
            'claim': claim,
            'notification': True,
        }
        return request.render("setu_claims_from_website.show_claim_view_form", vals)

    @http.route(['/my/claims/<int:order_id>'], type='http', auth="user", website=True)
    def portal_claims_page(self, order_id=None, **kwargs):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: managing the route for claim.
        """
        claim_view = request.env['crm.claim'].sudo().search([('id', '=', order_id)])
        values = {
            'claim': claim_view
        }
        return request.render('setu_claims_from_website.show_claim_view_form', values)

    def _prepare_home_portal_values(self, counters):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: adding count of claims to related user.
        """
        values = super()._prepare_home_portal_values(counters)
        total_claims = request.env['crm.claim'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])
        if 'claim_counts' in counters:
            values['claim_counts'] = len(total_claims)
        return values
