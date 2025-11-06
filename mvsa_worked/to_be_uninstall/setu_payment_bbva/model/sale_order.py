from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_reference = fields.Char(string="Payment Reference")
    payment_date = fields.Datetime(string="Payment Date")
    payment_method = fields.Char(string="Payment Method")
    card_holder_name = fields.Char(string="Card Holder Name")
    card_number = fields.Char(string="Card Number")
    authorization = fields.Char(string="Authorization")
    installments = fields.Char(string="Installments")
    payment_state = fields.Selection([('approved','Approved'),
                                      ('refused','Refused'),
                                      ('pending','Pending')],"Payment State")
    hmac_created_without_authorization = fields.Char(string="Hmac Created")
    hmac_created = fields.Char(string="Hmac Created With response")
    hmac_received = fields.Char(string="Hmac Received")
    folio = fields.Char(string="Folio")
    payment_folio = fields.Char(string="Payment folio")