# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


class TransportShipment(models.Model):
    _inherit = 'transport.shipment'

    #changes in existing field. Task: Migration from V16 to V18. #Jatin
    code = fields.Char(copy=False)
    status = fields.Selection(copy=False)
    shipment_tracking_ids = fields.One2many(copy=True)
    transport_do_ids = fields.One2many(copy=True)

    #New added fields. Task: Migration from V16 to V18. #Jatin
    beginning_of_load_date_and_time = fields.Datetime(string="Beginning Of Load Date And Time")
    ending_of_load_date_and_time = fields.Datetime(string="Ending Of Load Date And Time")
    load_execution_responsible = fields.Many2one("res.partner", string="Load Execution Responsible")
    cutover_date = fields.Datetime(string="Cutover Date")
    freight_responsible_id = fields.Many2one('hr.employee', string="Freight Responsible")
    delivery_person_signature = fields.Binary(string="Delivery Person Signature")
    shipping_staff_signature = fields.Binary(string="Shipping Staff Signature")


    def update_beginning_of_load_date_and_time(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 20/03/25
            Task: Migration from V16 to V18.
            Purpose: Update Beginning of load date and time.
        """
        self.beginning_of_load_date_and_time = datetime.now()

    def update_ending_of_load_date_and_time(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 20/03/25
            Task: Migration from V16 to V18.
            Purpose: Update Ending of load date and time.
        """
        self.ending_of_load_date_and_time = datetime.now()
        
    def shipment_ship(self):
        """
            ***Override Method***
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose:
            1) set current date in this field "x_studio_fecha_de_entrega".
            2) as we extend the module we need to perform the operation in shipping button as per the point - C in above url, here we manage the separate shipment records for Prepared By filled and not filled.
        """
        for rec in self:
            rec.status = 'ship'
            for do in rec.transport_do_ids:
                if do.status == 'draft' and do.prepared_by_id:
                    do.status = 'ship'
                    do.name.x_studio_fecha_de_envio = fields.datetime.now()

            without_prepared_id_line = rec.transport_do_ids.filtered(lambda line: not line.prepared_by_id)
            if without_prepared_id_line:
                prepare_vals = [
                        (0, 0, {
                            'name': line.name.id,
                            'so_id': line.so_id.id,
                            'partner_shipping_id': line.partner_shipping_id.id,
                            'source_location_id': line.source_location_id.id,
                            'destination_location_id': line.destination_location_id.id,
                            'shipping_carrier_id': line.shipping_carrier_id.id,
                            'package_count': line.package_count,
                            'pallet_count': line.pallet_count,
                            'box_count': line.box_count,
                            'carrier_tracking_ref': line.carrier_tracking_ref,
                            'delivery_address': line.delivery_address,
                            'status': line.status,
                            'prepared_by_id': line.prepared_by_id.id

                        })
                        for line in without_prepared_id_line
                    ]
                without_prepared_id_line.unlink()
                new_shipment_id = rec.copy(default={
                    'transport_do_ids': prepare_vals
                })
                # without_prepared_id_line.unlink()
                # new_shipment_id.transport_do_ids.filtered(lambda line: line.prepared_by_id).unlink()
                rec.message_post(
                    body=_(
                        f"Here are new shipment are created because there are some without Prepared By filled lines, and new shipment is {new_shipment_id.code}."
                    )
                )

    def shipment_delivered(self):
        """
            ***Override Method***
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: set current date in this field "x_studio_fecha_de_entrega"
        """
        for rec in self:
            rec.status = 'done'
            rec.vehicle_id.odometer = rec.odometer_end
            for do in rec.transport_do_ids:
                if do.status == 'in_transit':
                    do.status = 'done'
                    do.name.x_studio_fecha_de_entrega = fields.datetime.now()