from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    preparation_date = fields.Datetime(compute='_get_preparation_date')
    create_confirm_diff = fields.Float(string='Confirmation Duration',
                                       help="Difference in hours between order confirmed and customer confirmed.",
                                       copy=False, default=0)
    customer_confirmation_date = fields.Datetime(string="Customer Confirmation Date",copy=False)
    customer_confirmation_diff = fields.Float(string='Customer Confirmation Duration',
                                              help="Difference in hours between order created and it confirm by customer.",
                                              copy=False, default=0)
    date_order_received = fields.Datetime(string='Date Order Received')
    invoice_ref_id = fields.Many2one('account.move', string="Invoice Date Reference")

    def _get_preparation_date(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: set preparation date of out type picking
        """
        _logger.debug("Compute _get_preparation_date method start")
        preparation_date = False
        pickings = self.picking_ids.filtered(lambda x: x.state != 'cancel' and x.location_dest_id.usage == 'customer')
        for pick in pickings:
            preparation_date = pick.preparation_date
        self.preparation_date = preparation_date
        _logger.debug("Compute _get_preparation_date method end")

    def set_customer_confirmation_date(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: button to set current date while normal sale order but when if sale order from website then customer condirmation date will filled up automatically,
                    this is for customer confirmation
        """
        for record in self:
            record.customer_confirmation_date = datetime.now()


    def action_confirm(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: (1) check whether customer confirmation date is not set then it will raise an error.
                     (2) customer_confirmation_diff field is calculated time duration between sale order creation and customer confirmation date.
                     (3) create_confirm_diff field is calculated time duration between confirm date of sale order and customer confirmation date.
            Solved issue : To show Warning when Customer Confirmation Date is not mention while creating sale.orders(uncomment the code of warning)
        """

        res = super().action_confirm()
        resource_obj = self.env['resource.calendar'].sudo()
        confirmation_date = self.date_order
        for record in self:
            if record.website_id and not record.customer_confirmation_date:
                payment_transaction_records = self.env['payment.transaction'].search(
                    [('sale_order_ids', '=', record.id)])
                if payment_transaction_records:
                    record.customer_confirmation_date = max(payment_transaction_records.mapped('create_date'))
            if not record.customer_confirmation_date and not record.meli_order_id:
                raise ValidationError(_("Please enter customer confirmation date"))
            create_date = record.create_date
            confirmation_date = record.date_order
            customer_confirmation = record.customer_confirmation_date or datetime.now()
            total_hours_customer_confirm = resource_obj.get_shift_wise_hours(create_date, customer_confirmation)
            total_hours_confirm = resource_obj.get_shift_wise_hours(customer_confirmation, confirmation_date)
            record.customer_confirmation_diff = total_hours_customer_confirm
            record.create_confirm_diff = total_hours_confirm
        return res

    def calculate_total_processing_hours(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: (1) cron (Re-calculate Sales Time) method
                     (2) recalculate data of sales time dashboard report
        """

        proceed_count = 0
        resource_obj = self.env['resource.calendar'].sudo()
        for record in self:
            create_date = record.create_date
            date_order = record.date_order
            confirmation_date = record.date_order
            customer_confirmation = record.customer_confirmation_date
            if confirmation_date and customer_confirmation:
                record.customer_confirmation_diff = resource_obj.get_shift_wise_hours(create_date,customer_confirmation)
                record.create_confirm_diff = resource_obj.get_shift_wise_hours(customer_confirmation,confirmation_date)

            pickings = record.sudo().picking_ids.filtered(lambda x: x.picking_type_id.code == 'outgoing' and x.state == 'done')
            # total_invoices = record.sudo().invoice_ids and record.sudo().invoice_ids.filtered(lambda x: x.move_type == 'out_invoice' and x.state != 'draft') or False
            # invoice = total_invoices and self.env['account.move'].sudo().search([('id', 'in', total_invoices.ids)],
            #                                                                        order="id desc", limit=1) or False
            invoice = record.invoice_ref_id
            new_picking = pickings.filtered(lambda x: not x.is_cancellation_invoice)
            if new_picking:
                for picking in pickings:
                    picking_update_vals = {}
                    date_done = picking.date_done
                    preparation_date = picking.preparation_date
                    shipping_date = picking.x_studio_fecha_de_envio
                    confirmation_date = picking.scheduled_date
                    if confirmation_date and date_done:
                        confirm_date_done_diff = resource_obj.get_shift_wise_hours(confirmation_date, date_done)
                        picking_update_vals.update({'confirm_date_done_diff': confirm_date_done_diff})

                    if preparation_date and date_done:
                        date_invoice_preparation_date_diff = resource_obj.get_shift_wise_hours(date_done, preparation_date)
                        picking_update_vals.update(
                            {'date_invoice_preparation_date_diff': date_invoice_preparation_date_diff})
                    if preparation_date and shipping_date:
                        preparation_date_shipping_date_diff = resource_obj.get_shift_wise_hours(preparation_date,
                                                                                                shipping_date)
                        picking_update_vals.update(
                            {'preparation_date_shipping_date_diff': preparation_date_shipping_date_diff})

                    if picking.x_studio_fecha_de_envio and picking.x_studio_fecha_de_entrega:
                        picking.shipping_date_delivery_date_diff = resource_obj.get_shift_wise_hours(picking.x_studio_fecha_de_envio,
                                                                                                    picking.x_studio_fecha_de_entrega)

                    if invoice:
                        inv_create_date = invoice.create_date
                        if date_done and inv_create_date:
                            date_done_date_invoice_diff = resource_obj.get_shift_wise_hours(date_done, inv_create_date)
                            picking_update_vals.update({'date_done_date_invoice_diff': date_done_date_invoice_diff})
                    if picking_update_vals:
                        picking.write(picking_update_vals)
            if self:
                proceed_count += 1
                _logger.info(f"Processed  {proceed_count} out of {len(self)}")
        return True




