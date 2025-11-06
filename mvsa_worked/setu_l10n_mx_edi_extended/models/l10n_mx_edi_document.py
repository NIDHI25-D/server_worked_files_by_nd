from odoo import fields, models, api


class L10nMxEdiDocument(models.Model):
    _inherit = 'l10n_mx_edi.document'

    def _create_update_invoice_document_from_invoice(self, invoice, document_values):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/03/25
            Task: Migration to v18 from v16
            Purpose: set the l10n_mx_edi_cfdi_name field of the account and set public true of the created attachment for document.
        """
        result_document = super(L10nMxEdiDocument, self)._create_update_invoice_document_from_invoice(invoice,
                                                                                                 document_values)
        if result_document and result_document.move_id and result_document.attachment_id:
            result_document.move_id.write({'l10n_mx_edi_cfdi_name': result_document.attachment_id.name})
            result_document.attachment_id.write({'public': True})
        return result_document

    @api.model
    def _add_customer_cfdi_values(self, cfdi_values, customer=None, usage=None, to_public=False):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/03/25
            Task: Migration to v18 from v16
            Purpose: set a conditionally nombre value if there are commercial_partner_id is set
        """
        super()._add_customer_cfdi_values(cfdi_values, customer, usage, to_public)
        if 'receptor' in cfdi_values and 'customer' in cfdi_values.get('receptor'):
            invoice_customer_name = cfdi_values.get('receptor').get('nombre')
            invoice_customer = cfdi_values.get('receptor').get('customer')

            cfdi_values['receptor']['nombre'] = (
                invoice_customer_name if invoice_customer.commercial_partner_id else ''
            )
