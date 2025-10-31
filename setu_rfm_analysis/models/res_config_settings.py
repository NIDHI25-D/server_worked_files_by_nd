# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.models import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_dynamic_rules = fields.Boolean(implied_group='setu_rfm_analysis.group_dynamic_rules',
                                         string="Enable Dynamic Rules")
    group_sales_team_rfm = fields.Boolean(implied_group='setu_rfm_analysis.group_sales_team_rfm',
                                          string="Enable Sales Team Segments")
    module_setu_rfm_analysis_extended = fields.Boolean(string="Install PoS Sales")
    extended_module_in_registry = fields.Boolean(string='Extended Module in Registry',
                                                 config_parameter="setu_rfm_analysis.extended_module_in_registry")

    def open_actions_setu_rfm_configuration(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : The method ensures that the Point of Sale module is installed before allowing access to the RFM
        configuration action. If the module is not installed, it raises a validation error
        """
        point_of_sale = self.env['ir.module.module'].sudo().search(
            [('name', '=', 'point_of_sale')],
            limit=1)
        if point_of_sale.state != 'installed':
            raise ValidationError(_('In order to use this feature please install Point of Sale app first and try to '
                                    'activate this.'))
        action_values = self.sudo().env.ref('setu_rfm_analysis.actions_setu_rfm_configuration').sudo().read()[0]
        return action_values

