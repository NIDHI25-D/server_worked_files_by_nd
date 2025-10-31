from odoo import models,fields,api


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    return_location_id = fields.Many2one(
        'stock.location', 'Return Location',
        domain="['|', ('id', '=', original_location_id), '|', '&', ('return_location', '=', True), ('company_id', '=', False), '&', ('return_location', '=', True), ('company_id', '=', company_id)]")
    original_location_id = fields.Many2one('stock.location')

    def _prepare_picking_default_values(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 05/12/24
            Task: Migration from V16 to V18
            Purpose: to set picking idx to return_picking_id.
        """
        res = super()._prepare_picking_default_values()
        res.update({
            'return_picking_id': self.picking_id.id
        })
        return res

    @api.depends('picking_id')
    def _compute_moves_locations(self):
        """
            Author: nidhi@setuconsulting
            Date: 13/08/25
            Task: Return location on pickins {https://app.clickup.com/t/86dxef1c0}
            Purpose: to give default value for return_location_id
        """
        res = super()._compute_moves_locations()
        for wizard in self:
            if wizard.picking_id:
                location_id = wizard.picking_id.location_id.id
                if wizard.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                    location_id = wizard.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.id
                wizard.return_location_id = location_id
                wizard.original_location_id = wizard.picking_id.location_id.id
        return res

    def _prepare_picking_default_values_based_on(self, picking):
        """
            Author: nidhi@setuconsulting
            Date: 13/08/25
            Task: Return location on pickins {https://app.clickup.com/t/86dxef1c0}
            Purpose: prepare  default values of location_dest_id for picking
        """
        res = super()._prepare_picking_default_values_based_on(picking)
        # return_type = picking.picking_type_id.return_picking_type_id
        # if return_type and return_type.code == 'incoming':
        #     return res
        res['location_dest_id'] =  self.return_location_id.id or picking.location_id.id
        return res
