from odoo import models, fields, api, _


class ForecastCreatePoLineWizard(models.TransientModel):
    _name = 'forecast.create.po.line.wizard'
    _description = 'Forecast Create PO Line'

    po_line_wizard_id = fields.Many2one('forecast.create.po.wizard', string="Wizard", ondelete='cascade')
    po_line_warehouse_code = fields.Char(string="Code")
    po_line_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        domain="[('id', 'in', available_warehouse_ids)]"
    )
    po_line_qtb_value = fields.Float(string="QTB Qty")
    po_line_vendor_id = fields.Many2one('res.partner', string="Vendor", domain=[('supplier_rank', '>', 0)])
    available_warehouse_ids = fields.Many2many(
        'stock.warehouse', string='Available Warehouses', compute='_compute_available_warehouses'
    )
    related_po_ids = fields.Many2many(
        'purchase.order',
        string="Related Purchase Orders",
        compute='_compute_related_pos',
        store=False,
    )

    @api.depends('po_line_warehouse_code')
    def _compute_available_warehouses(self):
        """Restrict dropdown to warehouses in the forecast.wh.config for this code."""
        for line in self:
            whs = self.env['stock.warehouse']
            if line.po_line_warehouse_code:
                wh_match = self.env['stock.warehouse'].search([
                    ('code', '=', line.po_line_warehouse_code)
                ])
                if wh_match:
                    # If warehouse code directly exists, use it
                    whs = wh_match
                else :
                    config = self.env['forecast.wh.config'].search([('name', '=', line.po_line_warehouse_code)])
                    whs = config.warehouse_ids

            line.available_warehouse_ids = whs
            # set default warehouse (only if none set already)
            if whs and not line.po_line_warehouse_id:
                line.po_line_warehouse_id = whs[0]

    @api.depends('po_line_vendor_id', 'po_line_warehouse_id', 'po_line_wizard_id.po_forecast_line_id')
    def _compute_related_pos(self):
        """Find POs generated for the same vendor, warehouse, and forecast line today."""
        for line in self:
            # if not line.po_line_vendor_id or not line.po_line_warehouse_id:
            #     line.related_po_ids = False
            #     continue
            domain = [
                ('is_forecast_po', '=', True),
                ('partner_id', '=', line.po_line_vendor_id.id),
                ('picking_type_id', '=', line.po_line_warehouse_id.in_type_id.id),
                ('state', '=', 'draft'),
            ]
            # if forecast_line:
            #     domain.append(('forecast_line_id', '=', forecast_line.id))

            pos = self.env['purchase.order'].search(domain)
            line.related_po_ids = pos
