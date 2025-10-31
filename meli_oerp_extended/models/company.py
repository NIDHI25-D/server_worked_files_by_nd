from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    mercadolibre_invoice_address_id = fields.Many2one('res.partner', string="Invoice Address")
    responsible_person = fields.Many2one('hr.employee', string="Responsible Person")
