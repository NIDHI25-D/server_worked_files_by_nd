# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    responsible_person = fields.Many2one('hr.employee', string="Responsible Person", required=True)
    track_warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", compute="get_warehouse_location",
                                         store=True)
    check = fields.Boolean(default=False)

    comentarios_picking = fields.Text(string="Comentarios", related="sale_id.x_studio_comentarios")
    beginning_operation_date = fields.Datetime(string="Beginning Operation Date")
    beginning_of_load_date_and_time = fields.Datetime(string="Beginning Of Load Date And Time")
    ending_of_load_date_and_time = fields.Datetime(string="Ending Of Load Date And Time")
    operation_responsible = fields.Many2one("res.partner", string="Operation Responsible")
    load_execution_responsible = fields.Many2one("res.partner", string="Load Execution Responsible")
    order_fill_error_id = fields.Many2one('order.fill.error.catalog', string='Order Fill Error')
    improvement_points = fields.Selection(
        [("manifest_error", "Manifest Error"), ("duplicated_order", "Duplicated Order"), ("incomplete_invoice", "Incomplete Invoice"),
         ("non_collected_product", "Non Collected Product"), ("delivered_order", "Delivered Order"),
         ("without_document_for_shipping", "Without Document For Shipping")], string="Improvement Points")
    order_fill_error_picking_id = fields.Many2one('order.fill.error.picking', string='Cancellation Reason')

    @api.depends('picking_type_id')
    def get_warehouse_location(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: set the Warehouse as per the operation type's warehouse.
        """
        for move in self:
            move.track_warehouse_id = move.picking_type_id.warehouse_id

    def button_validate(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: During the picking validate if any move line not set responsible person then raise validation error
        """
        for picking in self:
            responsible_person_not_set_product = picking.move_line_ids.filtered(lambda mv: not mv.responsible_person.id)
            if responsible_person_not_set_product:
                for rec in responsible_person_not_set_product:
                    raise ValidationError("Product %r has not set responsible person" % rec.product_id.name)
        return super(StockPicking, self).button_validate()

    def action_assign(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: If you try to check Availability double time then it will raise and confirm to you.
        """
        for picking in self:
            picking.check = True if picking.state == 'assigned' else False
            if picking.check:
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Double Confirmation'),
                    'res_model': 'show.pop.up',
                    'view_mode': "form",
                    'view_id': self.env.ref(
                        'stock_inv_ext.picking_button_check_availability_view_form').id,
                    'target': 'new',
                }
        return super(StockPicking, self).action_assign()

    def update_beginning_operation_date(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: update Beginning Operation Date field as per the current time when clicked on update button.
        """
        self.beginning_operation_date = datetime.now()

    def update_beginning_of_load_date_and_time(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: update Beginning Of Load Date And Time field as per the current time when clicked on update button.
        """
        self.beginning_of_load_date_and_time = datetime.now()

    def update_ending_of_load_date_and_time(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: update Ending Of Load Date And Time field as per the current time when clicked on update button.
        """
        self.ending_of_load_date_and_time = datetime.now()

    def action_cancel(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: When user clicks on the cancel button of Picking (transfers), wizard will be opened (view_wizard_cancel_reason_form).
                     The Wizard will ask for the order_fill_error_picking and this field : order_fill_error_picking will be set in the picking's field order_fill_error_picking
                     (which was already mentioned in the picking)
        """
        if self.order_fill_error_picking_id:
            return super(StockPicking, self).action_cancel()
        else :
            return {
                    'name': _('Cancel Reason'),
                    'view_mode': 'form',
                    'res_model': 'wizard.cancel.reason',
                    'view_id': self.env.ref('stock_inv_ext.view_wizard_cancel_reason_form').id,
                    'type': 'ir.actions.act_window',
                    'target': 'new'
                }
