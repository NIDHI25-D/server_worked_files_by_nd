from odoo import fields, models, api


class CreateTmsShipmentWiz(models.TransientModel):
    _name = 'create.tms.shipment.wiz'
    _description = "Create TMS Shipment"

    route_id = fields.Many2one('transport.route', string="Transport Route")
    transporter_id = fields.Many2one('transporter.details', string="Transport via")
    responsible_id = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user.id)
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    driver_id = fields.Many2one('res.partner', domain=[('is_driver', '=', True)], string="Driver")

    def action_create_shipment(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: here from create button in wizard we create a shipment records as per the point - A from above url.
        """
        active_ids = self._context.get('active_ids')
        stock_picking_ids = self.env['stock.picking'].browse(active_ids)
        transport_shipment_obj = self.env['transport.shipment']
        record_vals_list = []
        record_vals = {
            "route_id": self.route_id.id,
            "transporter_id": self.transporter_id.id,
            "responsible": self.responsible_id.id,
            "vehicle_id": self.vehicle_id.id,
            "driver_id": self.driver_id.id,
            "transport_do_ids": [
                (0, 0, {'name': rec.id})
                for rec in stock_picking_ids]
        }
        record_vals_list.append(record_vals)
        transport_shipment_obj.create(record_vals_list)

