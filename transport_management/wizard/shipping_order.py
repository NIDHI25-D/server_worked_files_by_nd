# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class FleetVehicle(models.TransientModel):
    """Generate Shipping Order"""
    _name = 'ship.order'
    _description = __doc__

    transport_route_id = fields.Many2one('transport.route', string="Transport Route", required=True)
    transport_via = fields.Many2one('transporter.details', string="Transport via", required=True)

    pickup_date = fields.Datetime(string="Pickup Date", required=True)
    delivery_date = fields.Datetime(string="Expected Delivery Date", required=True)

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True)
    driver_id = fields.Many2one('res.partner', domain=[('is_driver', '=', True)], string="Driver", required=True)

    def generate_shipping_order(self):
        """generate shipping order"""
        so_ids = self._context.get('active_ids')
        SaleOrder = self.env['sale.order'].sudo()
        TransportDeliveryOrder = self.env['transport.delivery.order'].sudo()
        ship_data = {
            'route_id': self.transport_route_id.id,
            'transporter_id': self.transport_via.id,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id,
            'shipment_date': self.pickup_date,
            'delivery_date': self.delivery_date,
            'rate_per_km': self.transport_via.transport_charge,
            'distance': self.transport_route_id.distance,
            'total_cost': self.transport_via.transport_charge * self.transport_route_id.distance,
        }
        shipping_order = self.env['transport.shipment'].sudo().create(ship_data)
        for so in so_ids:
            order = SaleOrder.search([('id', '=', int(so))])
            if order.picking_ids:
                order.write({'shipment_id': shipping_order.id})
            for po in order.picking_ids:
                TransportDeliveryOrder.create({
                    'name': po.id,
                    'source_location_id': self.transport_route_id.source_location_id.id,
                    'destination_location_id': self.transport_route_id.destination_location_id.id,
                    'shipment_id': shipping_order.id,
                })
                # po.write({'shipment_id': shipping_order.id})
        mail_template = self.env.ref('transport_management.shipping_order_details_mail_template')
        if mail_template:
            mail_template.send_mail(shipping_order.id, force_send=True)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'transport.shipment',
            'target': 'current',
            'res_id': shipping_order.id,
        }
