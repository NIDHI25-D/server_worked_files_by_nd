from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_note_zero_tax = fields.Char("Invoice Notes (For Zero Tax)", config_parameter="setu_auto_validate_invoice.invoice_note_zero_tax")
    cancel_sale_order_days = fields.Integer("Cancel Sale Order Days", config_parameter="setu_auto_validate_invoice.cancel_sale_order_days")
    delete_sale_order_days = fields.Integer("Delete Sale Order Days", config_parameter="setu_auto_validate_invoice.delete_sale_order_days")
    cancel_sale_order_days_automatically = fields.Integer("Cancel Sale Order Days Automatically", config_parameter="setu_auto_validate_invoice.cancel_sale_order_days_automatically")
    disable_inv_automatic_sign = fields.Boolean( config_parameter="setu_auto_validate_invoice.disable_inv_automatic_sign",
        string='Disable Invoice Automatically signed',
        help="Check this to disable automatically sign invoice.")
    sign_user_id = fields.Many2one("res.users", string="Company User To Send Email",
                                      config_parameter="setu_auto_validate_invoice.sign_user_id")
