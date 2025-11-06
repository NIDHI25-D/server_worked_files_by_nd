from odoo import fields, models, api


class AccountInherit(models.Model):
    _inherit = 'account.move'

    def search_invoice_product(self, invoice_id=None):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: This method will give the product as per the invoice
        """
        invoice_id = self.sudo().browse(int(invoice_id))
        invoice_line_ids = invoice_id.invoice_line_ids
        dict = {}
        for invoice_line in invoice_line_ids:
            if invoice_line.product_id.type in ['consu']:
                dict.update({
                    invoice_line.product_id.id: invoice_line.product_id.display_name,
                })
        return dict

    def search_sale_team(self, invoice_id=None):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: This method will assign the sales_id with the service agent mentioned in the team_id
        """
        invoice_id = self.sudo().browse(int(invoice_id))
        team_id = invoice_id.team_id
        return {'sale_team': team_id.id, 'name': team_id.serviceagent_id.name}

    @api.model
    def l10n_mx_edi_retrieve_attachments(self):
        '''Retrieve all the cfdi attachments generated for this invoice.

        :return: An ir.attachment recordset
        '''
        self.ensure_one()
        if not self.l10n_mx_edi_cfdi_uuid:
            return []
        domain = [
            ('res_id', '=', self.id),
            ('res_model', '=', self._name),
            ('public', '=', True),
            ('name', '=', self.l10n_mx_edi_cfdi_name)]
        return self.env['ir.attachment'].sudo().search(domain)

    @api.model
    def l10n_mx_edi_retrieve_last_attachment(self):
        attachment_ids = self.sudo().l10n_mx_edi_retrieve_attachments()
        return attachment_ids and attachment_ids[0].sudo() or attachment_ids
