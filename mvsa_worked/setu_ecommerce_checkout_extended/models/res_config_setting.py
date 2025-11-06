from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ram_hcategory_id = fields.Many2one(
        comodel_name='res.partner.hcategory',
        config_parameter='setu_ecommerce_checkout_extended.ram_hcategory_id',
        string='Category',
    )
    partners_to_consider_after_date = fields.Datetime(string='Partners to consider after date',
                                                  config_parameter='setu_ecommerce_checkout_extended.partners_to_consider_after_date')
