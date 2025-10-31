# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_cost = fields.Float(string="Delivery cost",copy=False)
    packages_confirmed = fields.Integer(string="Packages")
    pallets_confirmed = fields.Integer(string="Pallets")
    payment_state = fields.Selection([('paid', 'Paid'), ('to_pay', 'To Pay'), ('tm', 'TM'), ('gscli', 'GSCLI')],
                                     string="Payment state",copy=False)
    x_studio_detener_factura = fields.Boolean(string="Detener Factura", readonly=True)
    cliente_mostrador = fields.Boolean(string="Cliente Mostrador", related='sale_id.mostrador')
    paid_invoice = fields.Boolean(string="Paid Invoice", default=False)
    invoice_number = fields.Char(string="Invoice Number")
    shipping_incident_ids = fields.Many2many('shipping.incident', 'stock_picking_shipping_incident_rel', 'incident_id',
                                             'picking_id', string="Shipping Incident")
    res_person_id = fields.Many2one('hr.employee', string="Responsible For The Shipment",copy=False)
    authorized_shipment_date = fields.Datetime(string="Authorized Shipment", copy=False)

    def set_authorized_shipment_date(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 02/01/25
            Task: Migration from V16 to V18 (https://app.clickup.com/t/86duencrc { Create an "Authorized Shipping" field in Stock Picking })
            Purpose: Button to set current date while normal sale order but when if sale order from website then customer confirmation date will filled up automatically,
                    this is for customer confirmation
        """
        for record in self:
            record.authorized_shipment_date = datetime.now()
