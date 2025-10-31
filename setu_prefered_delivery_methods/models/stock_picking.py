from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipping_carrier_id = fields.Many2one('shipping.carrier')
    package_picking_id = fields.Many2one('shipping.carrier', string="Package")
    pallet_picking_id = fields.Many2one('shipping.carrier', string="Pallet")
    overdimensioned_picking_id = fields.Many2one('shipping.carrier', string="Overdimensioned")
    available_carrier_ids = fields.Many2many("delivery.carrier", compute='_compute_available_carrier_as_per_prefer',
                                             string="Available Carriers As Per Prefer", store=True, precompute=True)

    @api.depends('partner_id')
    def _compute_available_carrier_as_per_prefer(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 06/01/25
            Task: Migration from V16 to V18 (https://app.clickup.com/t/86dqut9z1)
            Purpose: display only shipping methods as per the customer Configuration.
        """
        for rec in self:
            carriers = self.env['delivery.carrier'].search([])
            rec.available_carrier_ids = carriers.available_carriers(rec.partner_id,
                                                                    rec.sale_id) if rec.partner_id and rec.sale_id else carriers

    @api.onchange('partner_id')
    def onchange_method_to_assign_carrier(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 06/01/25
            Task: Migration from V16 to V18
            Purpose: This method will be called when the partner of sale_order->Delivery(before validating) is changed.
                     Then, when a user clicks on the carrier field of the stock.picking, it will get the carrier name
                     selected in their Preferred delivery method.
        """
        res = {}
        if self.partner_id.preferred_delivery_method_ids:
            domain = {'carrier_id': [('id', 'in', self.partner_id.preferred_delivery_method_ids.ids)]}
            return {'domain': domain}
        return res

    @api.model_create_multi
    def create(self, vals):
        """
            Author: jay.garach@setuconsulting.com
            Date: 06/01/25
            Task: Migration from V16 to V18
            Purpose: Adding custom field while creating picking.
        """
        res = super(StockPicking, self).create(vals)
        for record in res:
            if record.partner_id.package_partner_id or record.partner_id.pallet_partner_id or record.partner_id.overdimensioned_partner_id:
                record.write({
                    'package_picking_id': record.partner_id.package_partner_id,
                    'pallet_picking_id': record.partner_id.pallet_partner_id,
                    'overdimensioned_picking_id': record.partner_id.overdimensioned_partner_id})
                sale_id = self.env['sale.order'].search([('name', '=', record.origin)])
                if sale_id:
                    record.write({'carrier_id': sale_id.carrier_id,
                                  'shipping_carrier_id': sale_id.shipping_carrier_id})
            return res

    def _l10n_mx_edi_get_cartaporte_pdf_values(self):
        """
             Author: nidhi@setconsulting.com
             Date: 13/10/25
             Task: Improvements to the delivery guide report {https://app.clickup.com/t/86dxwk0z8} ==> {https://app.clickup.com/t/86dxwk0z8?comment=90170153648358}
             Purpose: exclude the locality codes and only show the name.Remove the colony code and show the name colony.
         """
        res = super()._l10n_mx_edi_get_cartaporte_pdf_values()
        warehouse_partner = self.picking_type_id.warehouse_id.partner_id
        origin_partner = self.partner_id if self.picking_type_code == 'incoming' else warehouse_partner
        destination_partner = self.partner_id if self.picking_type_code == 'outgoing' else warehouse_partner

        res['origen_domicilio']['municipio'] = origin_partner.city
        res['origen_domicilio']['colonia'] = origin_partner.l10n_mx_edi_colony

        res['destino_domicilio']['municipio'] = destination_partner.city
        res['destino_domicilio']['colonia'] = destination_partner.l10n_mx_edi_colony
        return res
