from odoo import models, fields, api, _, registry, SUPERUSER_ID
import logging
from datetime import datetime,timedelta
_logger = logging.getLogger("create_invoice_of_done_orders")
_cancel_logger = logging.getLogger("cancel_sale_orders")
_delete_logger = logging.getLogger("delete_sale_orders")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # l10n_mx_edi_payment_method_id = fields.Many2one('l10n_mx_edi.payment.method',
    #                                                 string='Payment Way') fulfilled in native.

    is_invoice_create_from_cron = fields.Boolean()
    disable_invoice_auto_sign = fields.Boolean(string="Disable Invoice Automatically Signed", copy=False)

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
            Author: siddharth@setuconsulting
            Date: 11/04/25
            Task: mvsa migration
            Purpose: auto validate invoice based on configuration
        """
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final,date=date)
        invoice_note = self.env['ir.config_parameter'].sudo().get_param(
            'setu_auto_validate_invoice.invoice_note_zero_tax') or False

        for invoice in invoices:
            if invoice_note and 0.0 in invoice.invoice_line_ids.mapped('tax_ids').mapped('amount'):
                self.env['account.move.line'].create({'name': invoice_note,
                                                      'display_type': 'line_note',
                                                      'move_id': invoice.id})
            if invoice.filtered(
                    lambda x: x.move_type == 'out_invoice' and x.currency_id.id == self.env.user.company_id.currency_id.id):
                disable_inv_sign_check = self.env['ir.config_parameter'].sudo().get_param(
                    'setu_auto_validate_invoice.disable_inv_automatic_sign') or False
                documents = hasattr(invoice.partner_id, 'disable_inv_automatic_sign') and invoice.filtered(
                    lambda doc: not doc.partner_id.disable_inv_automatic_sign) or False
                if self.disable_invoice_auto_sign:
                    return invoices
                if disable_inv_sign_check or not documents:
                    return invoices
                invoice.action_post()
        return invoices


    def _get_invoiceable_lines(self, final=False):
        """
            Author: siddharth@setuconsulting
            Date: 11/04/25
            Task: mvsa migration
            Purpose: remove lines move which are having unit price as 0.00 or reward line or delivery line
        """
        lines = super(SaleOrder, self)._get_invoiceable_lines(final=final)
        delivery_line_with_no_price = lines.filtered(lambda l: (not l.is_reward_line and (
                    (l.product_id.type == 'service' or l.is_delivery) and l.price_unit == 0.0)))
        return lines-delivery_line_with_no_price

    def cron_auto_create_invoices(self, limit=100):
        """
            Author: siddharth@setuconsulting
            Date: 11/04/25
            Task: mvsa migration
            Purpose: auto create invoice of confirmed and delivered orders
        """
        _logger.info(f"{limit}-------create invoice cron")
        query = f"""select so.id
                    from 
                    sale_order_line sol
                    join sale_order so on so.id = sol.order_id
                    where (so.is_invoice_create_from_cron = 't' OR so.amazon_channel = 'fba') and so.state not in ('draft','sent','cancel') and sol.qty_delivered > 0 and sol.qty_invoiced < sol.qty_delivered 
                    group by so.id 
                    order by so.create_date desc
                    limit {limit}"""
        self.env.cr.execute(query)
        sale_orders = self.env.cr.fetchall()
        total_orders = len(sale_orders)
        for count, lso in enumerate(sale_orders, start=1):
            lso = self.env['sale.order'].browse(lso[0])
            try:
                inv = lso._create_invoices()
                _logger.info(f"Invoice Created {inv.name} for order {lso.id}-{lso.name}")
            except Exception as e:
                _logger.exception(f"ERROR while processing order:{lso.id}-{lso.name} {e}")
                continue
            lso.is_invoice_create_from_cron = False
            _logger.info(f"Processed order {lso.id}-{lso.name} {count} out of {total_orders}")

    def cancel_sale_order(self):
        """
            Author: siddharth@setuconsulting
            Date: 11/04/25
            Task: mvsa migration
            Purpose: cances orders based on configuration which are having state of draft and sent and not from monthly proposal sale order
        """
        current_date = datetime.now().date()
        config_date = self.env['ir.config_parameter'].sudo().get_param(
            'setu_auto_validate_invoice.cancel_sale_order_days') or 0
        if config_date:
            post_date = current_date - timedelta(days=int(config_date))

            sale_orders = self.env['sale.order'].search([('state','in',['draft','sent']),('create_date','<',post_date)])
            if sale_orders  and hasattr(sale_orders, 'is_monthly_proposal'):
                sale_orders = sale_orders.filtered(lambda x:not x.is_monthly_proposal)
            if sale_orders:
                for i in sale_orders:
                    i._action_cancel()
                    _cancel_logger.info(f"Sale Order {i.name} Is Cancelled")
            else:
                _cancel_logger.info(f"No Sale Order Found For Cancel It")

    def delete_sale_order(self):
        """
                Author: siddharth@setuconsulting
                Date: 11/04/25
                Task: mvsa migration
                Purpose: delete orders based on configuration which are having state of cancel
        """
        current_date = datetime.now().date()
        config_date = self.env['ir.config_parameter'].sudo().get_param(
            'setu_auto_validate_invoice.delete_sale_order_days') or 0
        if config_date:
            post_date = current_date - timedelta(days=int(config_date))
            sale_orders = self.env['sale.order'].search([('state', '=', 'cancel'), ('create_date', '<', post_date)])
            if sale_orders:
                for i in sale_orders:
                    _delete_logger.info(f"Sale Order {i.name} Is Deleted")
                    i.unlink()
            else:
                _delete_logger.info(f"No Sale Order Found For Delete It")

    def cancel_sale_order_automatically(self):
        """
            Author: siddharth@setuconsulting
            Date: 11/04/25
            Task: https://app.clickup.com/t/86drgebn8
            Purpose: cancel sale orders as per the task requirement
        """
        current_date = datetime.now().date()
        config_date = self.env['ir.config_parameter'].sudo().get_param(
            'setu_auto_validate_invoice.cancel_sale_order_days_automatically') or 0
        if config_date:
            post_date = current_date - timedelta(days=int(config_date))
            sale_orders = self.env['sale.order'].search(
                [('create_date', '<', post_date),('locked', '=', True),
                 ('delivery_status', 'in', ['full'])])
            if sale_orders and  hasattr(sale_orders, 'is_preorder'):
                sale_orders = sale_orders.filtered(lambda x:not x.is_preorder and not x.is_presale)
            if sale_orders:
                for so in sale_orders:
                    if all(p.qty_delivered == 0 and p.qty_invoiced == 0 for p in so.order_line):
                        so._action_cancel()
                        _cancel_logger.info(f"Sale Order {so.name} Is Cancelled")
            else:
                _cancel_logger.info(f"No Sale Order Found For Cancel It")