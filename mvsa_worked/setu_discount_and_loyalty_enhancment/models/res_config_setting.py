from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    df_unspsc_code_id = fields.Many2one('product.unspsc.code', string="Default SAT Code",
                                        config_parameter="setu_discount_and_loyalty_enhancment.df_unspsc_code_id")
