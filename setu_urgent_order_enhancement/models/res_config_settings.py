# -*- coding: utf-8 -*-

from odoo import models, fields, api
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    urgent_orders_sales_team_ids = fields.Many2many('crm.team', string="Platforms")

    @api.model
    def get_values(self):
        """Get the values from settings."""
        res = super(ResConfigSettings, self).get_values()
        icp_sudo = self.env['ir.config_parameter'].sudo()
        urgent_orders_sales_team_ids = icp_sudo.get_param('setu_urgent_order_enhancement.urgent_orders_sales_team_ids')
        res.update(
            urgent_orders_sales_team_ids=[(6, 0, literal_eval(urgent_orders_sales_team_ids))] if urgent_orders_sales_team_ids else False,
        )
        return res

    def set_values(self):
        """Set the values. The new values are stored in the configuration parameters."""
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'setu_urgent_order_enhancement.urgent_orders_sales_team_ids',
            self.urgent_orders_sales_team_ids.ids)
        return res