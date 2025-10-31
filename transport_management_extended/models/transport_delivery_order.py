# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TransportDeliveryOrders(models.Model):
    _inherit = 'transport.delivery.order'

    shipment_id = fields.Many2one(ondelete='cascade')
    status = fields.Selection(copy=False)
    #added new fields. #20-March-25 #Jatin
    package_count = fields.Integer(string="Package count", related='name.package_count', store=True)
    pallet_count = fields.Integer(string="Pallet count", related='name.pallet_count', store=True)
    box_count = fields.Integer(string="Box count", related='name.box_count', store=True)
    partner_shipping_id = fields.Many2one(string="Delivery Address", related='name.partner_id')
    carrier_tracking_ref = fields.Char(string="Tracking Reference", related='name.carrier_tracking_ref',store=True)
    shipping_carrier_id = fields.Many2one('shipping.carrier', related='name.shipping_carrier_id', store=True, string="Carrier")
    prepared_by_id = fields.Many2one('hr.employee', string="Prepared By")

    @api.model
    def create(self, vals):
        """
            Author: nidhi@setconsulting.com
            Date: 15/10/25
            Task: Adding Enhancement Fields for Transport Management
            Purpose: Assign shipment_id to the picking when a transport.delivery.order is created,
            if its value is different from the existing one or is false.
        """
        delivery_order = super().create(vals)
        for delivery in delivery_order:
            if delivery.status == 'draft':
                delivery.name.preparation_date = fields.datetime.now()
            elif delivery.status == 'ship':
                delivery.name.x_studio_fecha_de_envio = fields.datetime.now()
            elif delivery.status == 'done':
                delivery.name.x_studio_fecha_de_entrega = fields.datetime.now()

            if delivery.name.shipment_id != delivery.shipment_id:
                delivery.name.shipment_id = delivery.shipment_id.id
        return delivery_order

    @api.onchange('carrier_tracking_ref')
    def onchange_carrier_tracking_ref(self):
        """
        Author: jatin.babariya@setuconsulting.com
        Date: 20/03/25
        Task: Migration from V16 to V18.
        Purpose: Within the "delivery orders" tab the field "carrier_tracking_ref" should be editable and the updated
                 information must be reflected in the "Tracking Reference" field which is mentioned in "additional info"
                tab of the Transfer Operation and vice versa.
        """
        for records in self:
            records.name.carrier_tracking_ref = records.carrier_tracking_ref

    @api.onchange('status', 'name')
    def _onchange_date_from_status(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 20/03/25
            Task: Migration from V16 to V18.
            Purpose: To set the fields in picking when state are change in transport.
        """
        if self.status == 'draft':
            self.name.preparation_date = fields.datetime.now()
        elif self.status == 'ship':
            self.name.x_studio_fecha_de_envio = fields.datetime.now()
        elif self.status == 'done':
            self.name.x_studio_fecha_de_entrega = fields.datetime.now()

    def unlink(self):
        """
            Author: nidhi@setconsulting.com
            Date: 15/10/25
            Task: Adding Enhancement Fields for Transport Management
            Purpose: in picking shipment_id become false if transport.delivery.order delete
        """
        for record in self:
            if record.name.shipment_id:
                record.name.shipment_id = False
        return super(TransportDeliveryOrders, self).unlink()