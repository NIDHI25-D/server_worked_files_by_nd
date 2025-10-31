from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    new_arrival_products_filter_days = fields.Integer(string="New Arrival Products Filter Days",
                                                      config_parameter="new_arrival_products_menu.new_arrival_products_filter_days")
