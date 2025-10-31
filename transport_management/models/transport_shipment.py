# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransportShipment(models.Model):
    """Transport Shipment"""
    _name = 'transport.shipment'
    _description = __doc__
    _rec_name = 'code'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'format.address.mixin']

    active = fields.Boolean(default=True)
    color = fields.Integer('Color Index', compute="_get_color_state")
    code = fields.Char(string="Number")
    tracking_ref_no = fields.Char(string="Waybill No")
    reference_no = fields.Char(string="Reference No	")

    route_id = fields.Many2one('transport.route', string="Transport Route", required=True)
    transporter_ids = fields.Many2many(related="route_id.transporter_ids")
    transporter_id = fields.Many2one('transporter.details', string="Transport via",
                                     domain="[('id','in',transporter_ids)]", required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True)
    driver_id = fields.Many2one('res.partner', domain=[('is_driver', '=', True)], string="Driver", required=True)
    responsible = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user.id)
    shipment_date = fields.Datetime(string="Pickup Date")
    delivery_date = fields.Datetime(string="Expected Date of Delivery")
    note = fields.Text(string="Note")
    terms = fields.Html(string="Terms & Conditions")

    rate_per_km = fields.Monetary(string="Rate", currency_field='currency_id', tracking=True)
    distance = fields.Float(string="Distance")
    total_cost = fields.Monetary(string="Total Charges", currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one("res.currency", string='Currency',
                                  default=lambda self: self.env.company.currency_id.id, readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    odometer_start = fields.Integer(string="Odometer Start")
    odometer_end = fields.Integer(string="Odometer End")

    status = fields.Selection([('draft', "Packing"), ('ship', "Shipping"), ('in_transit', "In Transit"),
                               ('done', "Delivered"), ('cancel', "Cancelled")], default='draft')

    shipment_tracking_ids = fields.One2many('shipment.tracking', 'shipment_id', string="Shipment Tracking")
    transport_do_ids = fields.One2many('transport.delivery.order', 'shipment_id', string="Delivery Orders")

    @api.depends('status')
    def _get_color_state(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: to set color based on status.
        """
        for rec in self:
            if rec.status == 'draft':
                rec.color = 0  # 1 danger 2 orange 10 green 4 info
            elif rec.status == 'done':
                rec.color = 10
            elif rec.status == 'in_transit':
                rec.color = 2
            elif rec.status == 'ship':
                rec.color = 4
            else:
                rec.color = 1

    @api.model_create_multi
    def create(self, vals_list):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Set Code by Sequence and Create Shipment.
        """
        for vals in vals_list:
            if vals.get('code', '') == '':
                vals['code'] = self.env['ir.sequence'].next_by_code('transport.shipment')
        shipment_id = super(TransportShipment, self).create(vals_list)
        return shipment_id

    def shipment_ship(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: to change status by clicking Shipping button.
        """
        for rec in self:
            rec.status = 'ship'
            for do in rec.transport_do_ids:
                if do.status == 'draft':
                    do.status = 'ship'

    def shipment_in_transit(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: to change status by clicking In Transit button.
        """
        for rec in self:
            rec.status = 'in_transit'
            for do in rec.transport_do_ids:
                if do.status == 'ship':
                    do.status = 'in_transit'

    def shipment_delivered(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: to change status by clicking In Delivered button.
        """
        for rec in self:
            rec.status = 'done'
            rec.vehicle_id.odometer = rec.odometer_end
            for do in rec.transport_do_ids:
                if do.status == 'in_transit':
                    do.status = 'done'

    def shipment_cancel(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: to change status by clicking In Cancel button.
        """
        for rec in self:
            rec.status = 'cancel'
            for do in rec.transport_do_ids:
                do.status = 'cancel'

    @api.model
    def get_shipment_stats(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Set Values in Dashboard.
        """
        transport_shipment = self.env['transport.shipment'].sudo()
        ts_all = transport_shipment.search_count([])
        ts_pack = transport_shipment.search_count([('status', '=', 'draft')])
        ts_ship = transport_shipment.search_count([('status', '=', 'ship')])
        ts_transit = transport_shipment.search_count([('status', '=', 'in_transit')])
        ts_done = transport_shipment.search_count([('status', '=', 'done')])
        ts_cancel = transport_shipment.search_count([('status', '=', 'cancel')])
        return {
            'all': ts_all,
            'pack': ts_pack,
            'ship': ts_ship,
            'transit': ts_transit,
            'done': ts_done,
            'cancel': ts_cancel,
            'orders_by_month': self.get_order_by_months(),
            'shipment_transporters': self.get_shipment_transporters(),
        }

    def get_order_by_months(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Set Values in Graph of Dashboard.
        """
        year = fields.Date.today().year
        year_str = str(year)
        data_dict = {
            '01/' + year_str: 0,
            '02/' + year_str: 0,
            '03/' + year_str: 0,
            '04/' + year_str: 0,
            '05/' + year_str: 0,
            '06/' + year_str: 0,
            '07/' + year_str: 0,
            '08/' + year_str: 0,
            '09/' + year_str: 0,
            '10/' + year_str: 0,
            '11/' + year_str: 0,
            '12/' + year_str: 0,
        }
        orders = self.env['sale.order'].search([('shipment_id', '!=', False)])
        for order in orders:
            if order.date_order.year == year:
                month_year = order.date_order.strftime("%m/%Y")
                data_dict[month_year] += order.amount_total
        return [list(data_dict.keys()), list(data_dict.values())]

    def get_shipment_transporters(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Set Values in Graph of Dashboard.
        """
        top_shipment_transporter = {}
        groups = self.env['transport.shipment'].read_group([], ['transporter_id'], ['transporter_id'],
                                                           orderby="transporter_id DESC")
        for group in groups:
            transporter_id = group['transporter_id']
            if transporter_id:
                transporter_record = self.env['transporter.details'].sudo().browse(transporter_id[0])
                transporter_name = transporter_record.name
                top_shipment_transporter[transporter_name] = group['transporter_id_count']
        sorted_transporter_data = sorted(top_shipment_transporter.items(), key=lambda item: item[1], reverse=True)
        transporters = [item[0] for item in sorted_transporter_data]
        shipment_counts = [item[1] for item in sorted_transporter_data]
        return [transporters, shipment_counts]

    # Onchange methods
    @api.onchange('transporter_id', 'route_id')
    def get_transport_route_details(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Get Transport Route Details.
        """
        for rec in self:
            if rec.transporter_id:
                rec.rate_per_km = rec.transporter_id.transport_charge
            if rec.route_id:
                rec.distance = rec.route_id.distance
            if rec.transporter_id and rec.route_id:
                rec.total_cost = rec.rate_per_km * rec.distance

    @api.onchange('rate_per_km', 'distance')
    def get_transport_cost(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Set total_cost.
        """
        for rec in self:
            if rec.rate_per_km and rec.distance:
                rec.total_cost = rec.rate_per_km * rec.distance

    @api.onchange('route_id')
    def _onchange_route_id(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Set Transport id False.
        """
        for rec in self:
            rec.transporter_id = False

    @api.onchange('transporter_id')
    def _onchange_transporter_id(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Set Vehicle id False.
        """
        for rec in self:
            rec.vehicle_id = False

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Set Vehicle id False.
        """
        for rec in self:
            rec.driver_id = False
            rec.odometer_start = rec.vehicle_id.odometer

    # Constrains
    @api.constrains('odometer_end','vehicle_id')
    def _check_odometer_end(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To raise validation if Odometer End is less then Odometer Start.
        """
        for rec in self:
            if rec.odometer_end < rec.odometer_start:
                raise ValidationError(_("The odometer end value cannot be lower than the odometer start."))

    @api.constrains('delivery_date', 'shipment_date')
    def _check_delivery_date(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To raise validation if Delivery Date is less then Pickup Date.
        """
        for rec in self:
            if rec.shipment_date and rec.delivery_date and rec.delivery_date < rec.shipment_date:
                raise ValidationError(_("The delivery date cannot be earlier than pickup date."))


class TransportShipmentTracking(models.Model):
    """Transport Shipment Tracking"""
    _name = 'shipment.tracking'
    _description = __doc__

    shipment_id = fields.Many2one('transport.shipment')
    tracking_date = fields.Date(string="Shipment Date")
    tracking_time = fields.Float(string="Time (24 Hrs. Format)")
    shipment_operation_id = fields.Many2one('shipment.operation', string="Shipment Operation")
    location = fields.Char(string="Location", required=True)

    @api.constrains('tracking_date')
    def _check_shipment_date(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Add constrains based on tracking_date field.
        """
        for rec in self:
            previous_shipment = self.env['shipment.tracking'].sudo().search(
                [('shipment_id', '=', rec.shipment_id.id), ('tracking_date', '!=', False),
                 ('id', '!=', rec.id), ('id',"<", rec.id)],
                order="create_date DESC", limit=1)
            next_shipment = self.env['shipment.tracking'].sudo().search(
                [('shipment_id', '=', rec.shipment_id.id), ('tracking_date', '!=', False),
                 ('id', '!=', rec.id), ('id',">", rec.id)],
                order="create_date", limit=1)
            if rec.shipment_id.shipment_date and  rec.tracking_date and rec.tracking_date < rec.shipment_id.shipment_date.date():
                raise ValidationError(_("The tracking date cannot be earlier than shipment pickup date."))
            elif previous_shipment and  rec.tracking_date and  rec.tracking_date < previous_shipment.tracking_date:
                raise ValidationError(_("The tracking date cannot be earlier than previous shipment tracking date."))
            elif next_shipment and  rec.tracking_date and rec.tracking_date > next_shipment.tracking_date:
                raise ValidationError(_("The tracking date cannot be after than next shipment tracking date."))


class ShipmentOperation(models.Model):
    """Transport Shipment Operation"""
    _name = 'shipment.operation'
    _description = __doc__

    name = fields.Char(string="Type of Operation", required=True)


class StockPicking(models.Model):
    """Stock Picking"""
    _inherit = 'stock.picking'
    _description = __doc__

    shipment_id = fields.Many2one('transport.shipment', string="Shipment")


class TransportDeliveryOrders(models.Model):
    """Transport Delivery Order"""
    _name = 'transport.delivery.order'
    _description = __doc__

    color = fields.Integer(compute='_get_color_state')
    name = fields.Many2one('stock.picking', string="Picking Order")
    so_id = fields.Many2one(related='name.sale_id', string="Sale Order")
    source_location_id = fields.Many2one('transport.location', string="Source Location")
    destination_location_id = fields.Many2one('transport.location', string="Destination Location")
    status = fields.Selection([('draft', "Packing"), ('ship', "Shipping"), ('in_transit', "In Transit"),
                               ('done', "Delivered"), ('cancel', "Cancelled")], default='draft')
    shipment_id = fields.Many2one('transport.shipment', string="Shipment")
    delivery_address = fields.Char(compute="_compute_delivery_address")

    @api.depends('status')
    def _get_color_state(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: to set color based on status.
        """
        for rec in self:
            if rec.status == 'draft':
                rec.color = 0  # 1 danger 2 orange 10 green 4 info
            elif rec.status == 'done':
                rec.color = 10
            elif rec.status == 'in_transit':
                rec.color = 2
            elif rec.status == 'ship':
                rec.color = 4
            else:
                rec.color = 1

    def _compute_delivery_address(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To compute delivery address.
        """
        for rec in self:
            address = ""
            if rec.name:
                if rec.name.partner_id.street:
                    address += f"{rec.name.partner_id.street} "
                if rec.name.partner_id.street2:
                    address += f"{rec.name.partner_id.street2} "
                if rec.name.partner_id.city:
                    address += f"{rec.name.partner_id.city}, "
                if rec.name.partner_id.state_id and rec.name.partner_id.state_id.name:
                    address += f"{rec.name.partner_id.state_id.name} "
                if rec.name.partner_id.zip:
                    address += f"{rec.name.partner_id.zip}, "
                if rec.name.partner_id.country_id and rec.name.partner_id.country_id.name:
                    address += f"{rec.name.partner_id.country_id.name}"
            rec.delivery_address = address


    @api.constrains('source_location_id', 'destination_location_id')
    def _check_source_destination_location(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To raise validation if Source Location and Destination Location Both are same.
        """
        for rec in self:
            if rec.source_location_id and rec.destination_location_id and rec.source_location_id.id == rec.destination_location_id.id:
                raise ValidationError(
                    _("Source location and destination location cannot be the same.\nPlease change any one location."))
