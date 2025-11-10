# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ForecastReportLine(models.Model):
    _name = 'forecast.report.line'
    _description = 'Forecast Report Line'
    _rec_name = 'name'

    # Link to forecast run
    history_id = fields.Many2one('forecast.report.history', string="Forecast History", required=True,
                                 ondelete='cascade')

    # Basic info
    product_id = fields.Many2one('product.product', string="Product")
    name = fields.Char(string="Name")
    sku = fields.Char(string="SKU")
    product_status = fields.Char(string="Status")
    supplier_id = fields.Many2one('res.partner', string="Supplier")

    product_category_id = fields.Many2one('product.category', string="Category")

    # Quantities
    shipments_in_transit = fields.Float(string="Shipments in Transit")
    fba_inbound = fields.Float(string="FBA Inbound")
    on_order = fields.Float(string="On Order")
    on_hand = fields.Float(string="On Hand")
    overall_total_units = fields.Float(string="Overall Total Units")
    total_units = fields.Float(string="Total Units")
    case_qty = fields.Float(string="Case Qty")

    # Flags
    has_product_update_details = fields.Boolean(string="Has Product Update Details")
    unit_cost = fields.Float(string="Unit Cost")

    # Total OOS / Daily Rates / DOI / Quantity to Buy (looped per period)
    total_daily_rate_7 = fields.Float(string="TDR7")
    total_daily_rate_15 = fields.Float(string="TDR15")
    total_daily_rate_30 = fields.Float(string="TDR30")
    total_daily_rate_45 = fields.Float(string="TDR45")
    total_daily_rate_60 = fields.Float(string="TDR60")
    total_daily_rate_90 = fields.Float(string="TDR90")
    total_daily_rate_120 = fields.Float(string="TDR120")
    total_daily_rate_180 = fields.Float(string="TDR180")

    doi_7 = fields.Integer(string="DOI7")
    doi_15 = fields.Integer(string="DOI15")
    doi_30 = fields.Integer(string="DOI30")
    doi_45 = fields.Integer(string="DOI45")
    doi_60 = fields.Integer(string="DOI60")
    doi_90 = fields.Integer(string="DOI90")
    doi_120 = fields.Integer(string="DOI120")
    doi_180 = fields.Integer(string="DOI180")

    quantity_to_buy_7 = fields.Integer(string="Qtb7")
    quantity_to_buy_15 = fields.Integer(string="Qtb15")
    quantity_to_buy_30 = fields.Integer(string="Qtb30")
    quantity_to_buy_45 = fields.Integer(string="Qtb45")
    quantity_to_buy_60 = fields.Integer(string="Qtb60")
    quantity_to_buy_90 = fields.Integer(string="Qtb90")
    quantity_to_buy_120 = fields.Integer(string="Qtb120")
    quantity_to_buy_180 = fields.Integer(string="Qtb180")

    total_sales_7 = fields.Float(string="TS7d")
    total_sales_15 = fields.Float(string="TS15d")
    total_sales_30 = fields.Float(string="TS30d")
    total_sales_45 = fields.Float(string="TS45d")
    total_sales_60 = fields.Float(string="TS60d")
    total_sales_90 = fields.Float(string="TS90d")
    total_sales_120 = fields.Float(string="TS120d")
    total_sales_180 = fields.Float(string="TS180d")
    total_sales_365 = fields.Float(string="TS365d")

    qtb_data_warehouse = fields.Json(string="QTB Data Warehouse", default={})
    b2b = fields.Float(string="B2B")
    remark = fields.Text(string="Remark")
    margin = fields.Float(string="Margin")

    applied_threshold_id = fields.Many2one('trigger.threshold',
                                           string="Applied Threshold",
                                           )
    applied_trigger_line_id = fields.Many2one('trigger.threshold.line',
                                              string='Applied Trigger Rule',
                                              ondelete='set null')

    applied_threshold_name = fields.Char(string="Applied Threshold Name")
    is_trigger_applied = fields.Boolean(string='Is Trigger Applied', default=False)
    warning_msg = fields.Char(string="Warning", readonly=True)
    trigger_row_color = fields.Char(string="Trigger Row Color")  # stores hex from trigger.main
    applied_trigger_id = fields.Many2one('trigger.main', string='Applied Trigger')
    qtb_po_buttons = fields.Html(string="Create POs", compute="_compute_qtb_po_buttons", sanitize=False)
    line_purchase_order_doi_days = fields.Integer(string="Purchase Order Doi days")
    qtb_data_warehouse_changes_json = fields.Text(string="Warehouse JSON Data")
    active_qtb_for_a_period = fields.Integer(string="Quantity To Buy",
                              compute="_compute_active_qtb_for_a_period",
                              store=False
                              )

    @api.depends('trigger_id')  # or however you track applied triggers
    def _compute_applied_color(self):
        for line in self:
            if line.applied_trigger_id:
                line.applied_trigger_color = line.applied_trigger_id.row_color
            else:
                line.applied_trigger_color = False

    def action_open_po_period_wizard(self):
        """Opens wizard prefilled with this line's data"""
        self.ensure_one()
        period = int(self.history_id.history_purchase_order_based_on_doi_id.days)
        return {
            'name': _('Create Purchase Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'forecast.create.po.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_po_forecast_line_id': self.id,
                'default_po_vendor_id': self.supplier_id.id,
                'default_po_product_id': self.product_id,
                'default_po_purchase_order_based_on_doi_days': period,
                'default_po_quantity_to_buy_as_per_selected_doi':self.active_qtb_for_a_period,
                # e.g. 90
            }
        }

    def action_open_po_wizard(self):
        """Open the PO creation wizard, pre-filling lines from qtb_data_warehouse."""
        wizard = self.env['forecast.create.po.wizard'].create({})
        ForecastLine = self.env['forecast.report.line']

        for line in ForecastLine.browse(self._context.get('active_ids', [])):
            vendor = line.supplier_id.id
            qtb_data = line.qtb_data_warehouse or {}

            for code, qty in qtb_data.items():
                #  Try to find a warehouse directly by code
                wh = self.env['stock.warehouse'].search([('code', '=', code)], limit=1)

                #  If not found, try via forecast.wh.config
                if not wh:
                    config = self.env['forecast.wh.config'].search([('name', '=', code)], limit=1)
                    wh = config.warehouse_ids[:1] if config and config.warehouse_ids else False

                #  Create PO Line Wizard entry
                self.env['forecast.create.po.line.wizard'].create({
                    'po_line_wizard_id': wizard.id,
                    'po_line_warehouse_code': code,
                    'po_line_warehouse_id': wh.id if wh else False,
                    'po_line_qtb_value': qty,
                    'po_line_vendor_id': vendor,
                })

        # Open the PO wizard form
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'forecast.create.po.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.depends_context('default_line_purchase_order_doi_days')
    def _compute_active_qtb_for_a_period(self):
        """Show only selected DOI quantity."""
        period = self.env.context.get('default_line_purchase_order_doi_days') or int(self.history_id.history_purchase_order_based_on_doi_id.days)
        for rec in self:
            if period == 7:
                rec.active_qtb_for_a_period = rec.quantity_to_buy_7
            elif period == 15:
                rec.active_qtb_for_a_period = rec.quantity_to_buy_15
            elif period == 30:
                rec.active_qtb_for_a_period = rec.quantity_to_buy_30
            elif period == 45:
                rec.active_qtb_for_a_period = rec.quantity_to_buy_45
            elif period == 60:
                rec.active_qtb_for_a_period = rec.quantity_to_buy_60
            elif period == 90:
                rec.active_qtb_for_a_period = rec.quantity_to_buy_90
            elif period == 120:
                rec.active_qtb_for_a_period = rec.quantity_to_buy_120
            elif period == 180:
                rec.active_qtb_for_a_period = rec.quantity_to_buy_180
            else:
                rec.active_qtb_for_a_period = 0.0
