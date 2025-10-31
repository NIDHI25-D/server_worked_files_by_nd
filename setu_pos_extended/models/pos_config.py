from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    approval_partner_for_invoice = fields.Many2one('res.partner', string='Supplier For Invoice Approval')
    enable_sale_team = fields.Boolean('Enable Sales Team')
    default_partner_id = fields.Many2one('res.partner', string="Select Customer")
