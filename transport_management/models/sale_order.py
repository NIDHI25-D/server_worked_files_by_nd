# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    """Sale Order"""
    _inherit = 'sale.order'
    _description = __doc__

    shipment_id = fields.Many2one('transport.shipment', string="Shipment Order")
    shipment_count = fields.Integer(compute="_get_shipment_count")

    def _get_shipment_count(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Get Shipment Count.
        """
        shipment_order = self.env['transport.shipment'].sudo()
        for record in self:
            record.shipment_count = shipment_order.search_count([('id', '=', record.shipment_id.id)])

    def get_shipments(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Shipment Record by Clicking on Shipments Button at sale order level.
        """
        self.ensure_one()
        domain = [('id', '=', self.shipment_id.id)]
        return {
            'name': _('Shipment Orders'),
            'res_model': 'transport.shipment',
            'domain': domain,
            'type': 'ir.actions.act_window',
            'views': [(False, 'kanban'), (False, 'list'), (False, 'form')],
            'view_mode': 'kanban'
        }

    def action_create_shipping(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Open wizard of Create Shipping.
        """
        ship_order_view = self.env.ref('transport_management.ship_order_wizard_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'ship.order',
            'view_id': ship_order_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }
