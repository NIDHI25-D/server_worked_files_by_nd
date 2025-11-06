# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, tools

from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    def _prepare_sale_order_values(self, partner_sudo):
        """
            Authour: nidhi@setconsulting
            Date: 9/12/2024
            Task: Migration from V16 to V18
            Purpose: This method is called when the sale order is created from the website.
                     Also it will enable: is_from_website to true as well as it will update fields : partner_invoice_id,warehouse_sugerido_id,warehouse_id
                     Once the sale order is created it will proceed to the same process of taking products from mentioned warehouse.
        """
        values = super(Website, self)._prepare_sale_order_values(partner_sudo=partner_sudo)
        values.update({'is_from_website': True})

        """
        uncomment this: partner_sudo.warehouse_sugerido_id when install marvelfields
        ----------------------------------------
        """
        # if partner_sudo.warehouse_sugerido_id:
        #     values.update({
        #         'warehouse_sugerido_id': partner_sudo.warehouse_sugerido_id.id or False,
        #         'warehouse_id': partner_sudo.warehouse_sugerido_id.id or False
        #     })
        if partner_sudo.parent_id:
            values.update({
                'partner_invoice_id': partner_sudo.parent_id.id or partner_sudo.id
            })
        return values
