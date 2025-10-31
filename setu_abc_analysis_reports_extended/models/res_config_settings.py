from odoo import api, exceptions, fields, models, _


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    upgrade_product_classification = fields.Selection([("3_months", '3 Months'),
                                                       ("6_months", "6 Months"),
                                                       ("year", "Year")], string="Product Upgrade Classification",
                                                      config_parameter='setu_abc_analysis_reports_extended.upgrade_product_classification')
