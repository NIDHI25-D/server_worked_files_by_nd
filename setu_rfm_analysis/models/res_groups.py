# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)
import odoo

ADMIN_USER_ID = odoo.SUPERUSER_ID


class Groups(models.Model):
    """ Update of res.groups class
        - if adding users from a group, check mail.channels linked to this user
          group and subscribe them. This is done by overriding the write method.
    """
    _inherit = 'res.groups'

    def write(self, vals, context=None):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date:
        Task: $Task_Name$
        Purpose: $Description$
        :param vals:
        :param context:
        :return:
        """
        enable_sales = self.env.ref('setu_rfm_analysis.group_sales_team_rfm').id
        dynamic_rules = self.env.ref('setu_rfm_analysis.group_dynamic_rules').id
        gp_to_append = self.env.ref('setu_rfm_analysis.group_rfm_show_team_conf').id
        has_enable_sales_group = self.env.user.has_group('setu_rfm_analysis.group_sales_team_rfm')
        has_dynamic_rules_group = self.env.user.has_group('setu_rfm_analysis.group_dynamic_rules')
        grp_user = self.env.ref('base.group_user')
        if 'implied_ids' in vals:
            if vals['implied_ids'][0][1] == enable_sales and has_dynamic_rules_group:
                vals['implied_ids'].append((vals['implied_ids'][0][0], gp_to_append))
            if vals['implied_ids'][0][1] == dynamic_rules and has_enable_sales_group:
                vals['implied_ids'].append((vals['implied_ids'][0][0], gp_to_append))
            if vals['implied_ids'][0][0] == 3:
                self.env.ref('setu_rfm_analysis.group_rfm_show_team_conf').write(
                    {'users': [(3, user.id) for user in grp_user.users]})

        write_res = super(Groups, self).write(vals)

        return write_res