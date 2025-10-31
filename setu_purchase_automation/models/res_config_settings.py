from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    po_tax_payment_days_configures = fields.Integer(string="Configure Tax payment days", config_parameter='setu_purchase_automation.po_tax_payment_days_configures', default=0)
    po_expected_arrival_date_automation = fields.Integer(string="Expected Arrival Date Automation", config_parameter='setu_purchase_automation.po_expected_arrival_date_automation', default=0)
    henco_api_url = fields.Char(string="Henco API", config_parameter='setu_purchase_automation.henco_api_url')
    henco_company = fields.Char(string="Company", config_parameter='setu_purchase_automation.henco_company')
    henco_customernum = fields.Integer(string="CustomerNum", config_parameter='setu_purchase_automation.henco_customernum')
    henco_linetype = fields.Char(string="LineType", config_parameter='setu_purchase_automation.henco_linetype')
    henco_level = fields.Char(string="Level", config_parameter='setu_purchase_automation.henco_level')
    henco_x_api_key = fields.Char(string="x-api-key", config_parameter='setu_purchase_automation.henco_x_api_key')
    henco_username = fields.Char(string="Henco Username", config_parameter='setu_purchase_automation.henco_username')
    henco_password = fields.Char(string="Henco Password", config_parameter='setu_purchase_automation.henco_password')
