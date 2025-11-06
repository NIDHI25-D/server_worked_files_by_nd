from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    approval_partner_for_invoice = fields.Many2one(related='pos_config_id.approval_partner_for_invoice', readonly=False)
    enable_sale_team = fields.Boolean(related='pos_config_id.enable_sale_team', readonly=False)
    pos_default_partner_id = fields.Many2one('res.partner', related='pos_config_id.default_partner_id', readonly=False)

