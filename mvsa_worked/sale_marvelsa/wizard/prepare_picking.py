from odoo import fields, models, api


class PreparePicking(models.TransientModel):
    _name = 'prepare.picking'
    _description = 'Prepare Picking'

    stock_pick_type_id = fields.Many2one('stock.picking.type', domain=lambda self: self._domain_show_stock_pick_type())

    def _domain_show_stock_pick_type(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 27/01/25
            Task: Migration to v18 from v16
            Purpose: prepare domain for a field stock picking type.
        """
        picking_id = self.env['stock.picking'].browse(self._context.get('active_id'))
        if picking_id:
            return [('is_enable_create_picking', '=', True), ('code', '=', picking_id.picking_type_id.code)]
        else:
            return []

    def create_picking(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 27/01/25
            Task: Migration to v18 from v16
            Purpose: create a transfer from a button Save in a wizard.
        """
        picking = self.env['stock.picking']
        picking_id = picking.browse(self._context.get('active_id'))
        if picking_id:
            picking_data = picking_id.copy_data()
            for pick in picking_data:
                pick.update({
                    'picking_type_id': self.stock_pick_type_id.id,
                    'location_id': self.stock_pick_type_id.default_location_src_id.id
                })
            picking.create(picking_data)
