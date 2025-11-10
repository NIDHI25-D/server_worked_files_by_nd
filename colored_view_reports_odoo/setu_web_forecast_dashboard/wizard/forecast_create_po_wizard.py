from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
import json


class ForecastCreatePoWizard(models.TransientModel):
    _name = 'forecast.create.po.wizard'
    _description = 'Forecast Purchase Order Wizard'

    po_forecast_line_id = fields.Many2one('forecast.report.line', string="Forecast Line")
    po_product_id = fields.Many2one('product.product', string="Product")
    po_vendor_id = fields.Many2one('res.partner', string="Vendor", domain=[('supplier_rank', '>', 0)], required=True)
    po_selection_type = fields.Selection([
        ('with_warehouse', 'With Warehouse'),
        ('without_warehouse', 'Without Warehouse'),
    ], string="PO Type", default='with_warehouse', required=True)

    po_line_ids = fields.One2many('forecast.create.po.line.wizard', 'po_line_wizard_id', string="Warehouse Lines")
    po_purchase_order_based_on_doi_days = fields.Integer(string="DOI Days")
    po_count = fields.Integer(string="Purchase Orders", compute='_compute_po_count', store=False)
    po_quantity_to_buy_as_per_selected_doi = fields.Integer(string="Quantity To Buy")
    po_forecast_date = fields.Date()

    @api.depends('po_line_ids.related_po_ids')
    def _compute_po_count(self):
        for wizard in self:
            all_pos = wizard.po_line_ids.mapped('related_po_ids')
            wizard.po_count = len(all_pos)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        forecast_line = self.env['forecast.report.line'].browse(self.env.context.get('default_po_forecast_line_id'))
        line_vals = []

        if forecast_line and forecast_line.qtb_data_warehouse:
            # handle JSON string
            data = forecast_line.qtb_data_warehouse
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except Exception:
                    data = {}

            for code, vals in data.items():
                # handle both float and dict structure
                if isinstance(vals, dict):
                    qty = vals.get('qty', 0.0)
                    vendor_id = vals.get('vendor_id', False)
                else:
                    qty = vals
                    vendor_id = forecast_line.supplier_id.id if forecast_line else False

                line_vals.append((0, 0, {
                    'po_line_warehouse_code': code,
                    'po_line_qtb_value': qty,
                    'po_line_vendor_id': vendor_id,
                }))

        res['po_line_ids'] = line_vals
        if forecast_line:
            res['po_product_id'] = forecast_line.product_id.id
            # res['po_count'] = self.env['purchase.order'].search_count([
            #     ('forecast_line_id', '=', forecast_line.id)
            # ])
        return res

    # This method auto-updates JSON when lines change
    @api.onchange('po_line_ids')
    def _onchange_po_line_ids(self):
        for wizard in self:
            save_data = {}
            for line in wizard.po_line_ids:
                save_data[line.po_line_warehouse_code] = {
                    'qty': line.po_line_qtb_value,
                    'vendor_id': line.po_line_vendor_id.id if line.po_line_vendor_id else False,
                }

            if wizard.po_forecast_line_id:
                wizard.po_forecast_line_id.qtb_data_warehouse = json.dumps(save_data)

    def action_view_related_pos(self):
        self.ensure_one()
        pos =self.po_line_ids.related_po_ids
        return {
            'name': _('Purchase Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', pos.ids)],
        }

    def action_create_po(self):
        """Creates one PO per warehouse line."""
        PurchaseOrder = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']
        forecast_line = self.po_forecast_line_id

        product = forecast_line.product_id
        if not product:
            raise UserError(_("No product found to create Purchase Order."))

        created_pos = []
        today = fields.Date.today()
        json_data = {}  # will store vendor+qty mapping per warehouse

        for line in self.po_line_ids:
            json_data[line.po_line_warehouse_code] = {
                'qty': line.po_line_qtb_value,
                'vendor_id': line.po_line_vendor_id.id if line.po_line_vendor_id else False,
            }

            if not line.po_line_vendor_id or line.po_line_qtb_value <= 0:
                continue

            existing_po = PurchaseOrder.search([
                ('is_forecast_po', '=', True),
                ('partner_id', '=', line.po_line_vendor_id.id),
                ('date_order', '>=', fields.Datetime.to_datetime(f"{today} 00:00:00")),
                ('date_order', '<=', fields.Datetime.to_datetime(f"{today} 23:59:59")),
                ('state', '=', 'draft'),
            ])

            purchase_order = False
            for po in existing_po:
                if po.picking_type_id == line.po_line_warehouse_id.in_type_id and po.partner_id.id == line.po_line_vendor_id.id:
                    purchase_order = po
                    break

            if not purchase_order:
                po_vals = {
                    'partner_id': line.po_line_vendor_id.id,
                    'date_order': fields.Datetime.now(),
                    'picking_type_id': line.po_line_warehouse_id.in_type_id.id,
                    'is_forecast_po': True,
                    'forecast_line_id': forecast_line.id,
                }
                purchase_order = PurchaseOrder.create(po_vals)
                created_pos.append(purchase_order.id)

            # Add this product line to the PO (new or existing)
            PurchaseOrderLine.create({
                'order_id': purchase_order.id,
                'product_id': product.id,
                'name': product.display_name,
                'product_qty': line.po_line_qtb_value,
                'product_uom': product.uom_po_id.id,
                'price_unit': product.standard_price or 0.0,
                'date_planned': fields.Datetime.now(),
            })
            if purchase_order.id not in created_pos:
                created_pos.append(purchase_order.id)
                # Link it back to the wizard line (to appear in related_po_ids)
            if purchase_order.state == 'draft':
                line.related_po_ids = [(4, purchase_order.id)]

        if len(created_pos) == 1:
            return {
                'name': _('Purchase Order'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': created_pos[0],
            }
        else:
            return {
                'name': _('Created Purchase Orders'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', created_pos)],
            }
