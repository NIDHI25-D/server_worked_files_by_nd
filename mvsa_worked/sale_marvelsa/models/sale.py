# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pickings_counter = fields.Char(string="Orders Done", compute='_get_pickings_counter')
    preparation_date = fields.Datetime(string="Preparation Date", compute='_get_preparation_date', store=True)
    date_invoice = fields.Date(string="Date Invoice", compute='_get_date_invoice')
    send_date = fields.Datetime(string="Shipment Date", compute='_get_send_date', store=True)
    carrier_tracking_ref = fields.Char(string="Tracking Reference", compute='_get_carrier_tracking_ref', store=True,
                                       search='_search_tracking_reference')
    x_studio_fecha_de_entrega = fields.Datetime(string="Picking Delivery Date", compute='_get_x_studio_fecha_de_entrega', store=True)
    delivery_auto = fields.Boolean(string="Delivery Automaticly", default=False)
    delivery_address = fields.Text(string="Delivery Address", compute='_get_delivery_address')
    destination_address = fields.Text(string="Destination Address", compute='_get_destination_address')
    shippment_info = fields.Text(string="Shipping Info", compute='_get_shippment_info')
    notes_info = fields.Text(string="Note", compute='_get_notes_info')
    is_terms_and_condition_accepted = fields.Boolean()
    terms_and_condition_date = fields.Date(string="Terms And Condition Accepted Date")
    carrier_id = fields.Many2one('delivery.carrier', string='Shipping Method')
    picking_origin = fields.Char(related='picking_ids.origin', string='Picking Source Document')

    @api.depends('picking_ids.x_studio_fecha_de_envio')
    def _get_send_date(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set a send date as per the pickings
        """
        _logger.debug("Compute _get_send_date method start")
        for order in self:
            x_studio_fecha_de_envio = False
            pickings = order.picking_ids.filtered(
                lambda x: x.state != 'cancel' and x.location_dest_id.usage == 'customer')
            for pick in pickings:
                x_studio_fecha_de_envio = pick.x_studio_fecha_de_envio
            order.send_date = x_studio_fecha_de_envio
        _logger.debug("Compute _get_send_date method end")

    def _get_date_invoice(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set a date_invoice as per the invoice_date
        """
        _logger.debug("Compute _get_date_invoice method start")
        for order in self:
            date_inv = order.order_line.mapped('invoice_lines').mapped('move_id').filtered(
                lambda r: r.move_type in ['out_invoice'] and r.state in ['posted']).mapped('invoice_date')
            order.date_invoice = date_inv[-1] if date_inv else False
        _logger.debug("Compute _get_date_invoice method end")

    @api.depends('picking_ids.preparation_date')
    def _get_preparation_date(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set a preparation date as per the pickings preparation date
        """
        _logger.debug("Compute _get_preparation_date method start")
        for order in self:
            preparation_date = False
            pickings = order.picking_ids.filtered(
                lambda x: x.state != 'cancel' and x.location_dest_id.usage == 'customer')
            for pick in pickings:
                preparation_date = pick.preparation_date
            order.preparation_date = preparation_date
        _logger.debug("Compute _get_preparation_date method end")

    @api.depends('picking_ids.carrier_tracking_ref')
    def _get_carrier_tracking_ref(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set a carrier_carrier_tracking_ref as per the pickings reference
        """
        _logger.debug("Compute _get_carrier_tracking_ref method start")
        for order in self:
            pickings = order.picking_ids.filtered(lambda
                                                      x: x.state != 'cancel' and x.location_dest_id.usage == 'customer' and x.carrier_tracking_ref != False)
            carrier_tracking_ref = ', '.join(pick.carrier_tracking_ref for pick in pickings)
            order.carrier_tracking_ref = carrier_tracking_ref
        _logger.debug("Compute _get_carrier_tracking_ref method end")

    # Used for search Tracking Reference
    def _search_tracking_reference(self, operator, value):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: search carrier_tracking_ref as per the below domains
        """
        if operator == 'ilike':
            ps = self.search([('state', '=', 'sale')]).filtered(lambda s: s.carrier_tracking_ref == value)
        return [('id', 'in', [x.id for x in ps] if ps else False)]

    @api.depends('picking_ids.x_studio_fecha_de_entrega')
    def _get_x_studio_fecha_de_entrega(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set a x_studio_fecha_de_entrega as per the pickings x_studio_fecha_de_entrega
        """
        _logger.debug("Compute _get_x_studio_fecha_de_entrega method start")
        for order in self:
            x_studio_fecha_de_entrega = False
            pickings = order.picking_ids.filtered(
                lambda x: x.state != 'cancel' and x.location_dest_id.usage == 'customer')
            for pick in pickings:
                x_studio_fecha_de_entrega = pick.x_studio_fecha_de_entrega
            order.x_studio_fecha_de_entrega = x_studio_fecha_de_entrega
        _logger.debug("Compute _get_x_studio_fecha_de_entrega method end")

    def _get_pickings_counter(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set a pickings_counter as per the pickings
        """
        _logger.debug("Compute _get_pickings_counter method start")
        for rec in self:
            pickings_counter = ""
            customer_location = self.env.ref('stock.stock_location_customers')
            qty_pickings = self.env['stock.picking'].sudo().search_count(
                [('sale_id', '=', rec.id), ('state', '!=', 'cancel'), ('location_id', '!=', customer_location.id)])
            qty_pick_done = self.env['stock.picking'].sudo().search_count(
                [('sale_id', '=', rec.id), ('state', '=', 'done'), ('location_id', '!=', customer_location.id)])
            pickings_counter = "{0}/{1}".format(qty_pick_done, qty_pickings)
            rec.pickings_counter = pickings_counter
        _logger.debug("Compute _get_pickings_counter method end")

    def get_invoiced_to_pay(self, partner_id):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set total_invoiced as per the partners total due
        """
        total_invoiced = 0
        total_invoiced = partner_id.total_due
        return total_invoiced

    def get_invoiced_count(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: get a invoice count as per the invoice_ids
        """
        invoice_count = 0
        for order in self:
            invoice_ids = order.order_line.mapped('invoice_lines').mapped('move_id').filtered(
                lambda r: r.move_type in ['out_invoice'] and r.state in ['open', 'in_payment', 'paid'])
            invoice_count = len(set(invoice_ids.ids))

        return invoice_count

    def _get_delivery_address(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set delivery_address as per the partner_shipping
        """
        _logger.debug("Compute _get_delivery_address method start")
        for order in self:
            get_addr = order.partner_shipping_id.sudo().with_context(show_address=True, html_format=False)._get_all_addr()[0]
            contact_type = get_addr.get('contact_type')
            street = get_addr.get('street')
            zip = get_addr.get('zip')
            city = get_addr.get('city')
            country = get_addr.get('country')
            order.delivery_address = f'{contact_type}\n{street}\n{zip}\n{city}\n{country}'
        _logger.debug("Compute _get_delivery_address method end")

    def _get_destination_address(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set a destination_address as per the partner_id address
        """
        _logger.debug("Compute _get_destination_address method start")
        for order in self:
            get_addr = order.partner_id.sudo().with_context(show_address=True, html_format=False)._get_all_addr()[0]
            contact_type = get_addr.get('contact_type')
            street = get_addr.get('street')
            zip = get_addr.get('zip')
            city = get_addr.get('city')
            country = get_addr.get('country')
            order.destination_address = f'{contact_type}\n{street}\n{zip}\n{city}\n{country}'
        _logger.debug("Compute _get_destination_address method end")

    def _get_shippment_info(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set a shippment_info as per the pickings packages, pallets, weight, weight
        """
        _logger.debug("Compute _get_shippment_info method start")
        packages = _("Packages:")
        pallets = _("Pallets:")
        weight = _("Weight:")
        for order in self:
            pickings = order.picking_ids.filtered(
                lambda x: x.state != 'cancel' and x.location_dest_id.usage == 'customer')
            shippment_info = ""
            for pick in pickings:
                shippment_info += "{0} {1}, \n{2}, \n{3} \n\n".format(packages, pallets, weight, pick.weight)
            order.shippment_info = shippment_info
        _logger.debug("Compute _get_shippment_info method end")

    def _get_notes_info(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set a notes_info as per the pickings note
        """
        _logger.debug("Compute _get_notes_info method start")
        for order in self:
            pickings = order.picking_ids.filtered(
                lambda x: x.state != 'cancel' and x.location_dest_id.usage == 'customer')
            notes_info = ""
            for pick in pickings:
                notes_info += "{0}\n\n".format(pick.note or "")
            order.notes_info = notes_info
        _logger.debug("Compute _get_notes_info method end")

    def validate_credit_limit(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set a dfactura,reason,delivry auto as per the customer_agrobolder_id and pricelists is credit or not
        """
        reason = ''

        sales = self.env['sale.order']
        current_date = datetime.today()
        init_date = datetime(current_date.year, current_date.month, 1)
        end_date = datetime(current_date.year, current_date.month, 1) + relativedelta(months=1, days=-1, hours=23,
                                                                                      minutes=59)
        dfactura = True
        delivery_auto = True

        if self.partner_id.id == self.env.user.company_id.customer_agrobolder_id.id or self.partner_id.parent_id.id == self.env.user.company_id.customer_agrobolder_id.id:
            self.sudo().write({'delivery_auto': delivery_auto})
            return reason

        if self.pricelist_id.is_credit:
            invoiced_to_pay = self.get_invoiced_to_pay(self.partner_id)
            sales_to_invoice = sales.sudo().search(
                [('partner_id', '=', self.partner_id.id), ('invoice_status', 'in', ('no', 'to invoice')),
                 ('state', '=', 'sale'), ('create_date', '>', init_date), ('create_date', '<', end_date)])
            sales_to_delivery = sales_to_invoice

            for so in sales_to_delivery:
                if so.get_invoiced_count() <= 0:
                    invoiced_to_pay += so.amount_total

            if invoiced_to_pay > self.partner_id.credit_limit:
                reason += "Le notificamos  que su límite de crédito se encuentra excedido. Favor de contactar a su ejecutivo de cobranza."
                dfactura = delivery_auto = False
            elif (invoiced_to_pay + self.amount_untaxed) > self.partner_id.credit_limit:
                reason += "El monto de esta compra excede su limite de credito"
                dfactura = delivery_auto = False

            self.sudo().write({'delivery_auto': delivery_auto})
        else:
            self.sudo().write({'dfactura': dfactura, 'delivery_auto': delivery_auto})

        return reason

    def get_balance_by_credit_limit(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: get a credit limit as per partner_data
        """
        credit_balance = invoiced_to_pay = 0
        sales = self.env['sale.order']
        current_date = datetime.today()

        if self.pricelist_id.is_credit:
            init_date = datetime(current_date.year, current_date.month, 1)
            end_date = datetime(current_date.year, current_date.month, 1) + relativedelta(months=1, days=-1, hours=23,
                                                                                          minutes=59)

            sales_to_invoice = sales.sudo().search(
                [('partner_id', '=', self.partner_id.id), ('invoice_status', 'in', ('no', 'to invoice')),
                 ('state', '=', 'sale'), ('create_date', '>', init_date), ('create_date', '<', end_date)])

            for so in sales_to_invoice:
                if so.get_invoiced_count() <= 0:
                    invoiced_to_pay += so.amount_total

            invoiced_to_pay += self.amount_total
            invoiced_to_pay += self.get_invoiced_to_pay(self.partner_id)
            credit_balance = (self.partner_id.credit_limit - invoiced_to_pay)

            if credit_balance < 0:
                self.sudo().write({'delivery_auto': False})

        return credit_balance

    def validate_total_due(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: set a delivery_auto as per the customer_agrobolder_id and partner's pricelist
        """
        reason = ''
        delivery_auto = True

        if self.partner_id.id == self.env.user.company_id.customer_agrobolder_id.id or self.partner_id.parent_id.id == self.env.user.company_id.customer_agrobolder_id.id:
            self.sudo().write({'delivery_auto': delivery_auto})
            return reason

        if self.partner_id.total_overdue > 0.0:
            reason = """
			Le informamos que cuenta con facturas vencidas.
			Favor de contactar a su ejecutivo de cobranza.
			"""
            delivery_auto = False

        if self.pricelist_id.is_credit == False:
            delivery_auto = False

        self.sudo().write({'delivery_auto': delivery_auto})
        return reason

    def auto_cancel_and_delete_sale_orders(self, active_test=False):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: Execute crons as per the configuration
        """
        current_date = datetime.today()
        current_day = datetime.today().day
        to_date = current_date + timedelta(days=-31)
        to_date = to_date.strftime('%Y-%m-%d %H:%M:%S')

        if active_test:
            self._cancel_and_delete_orders(to_date)
        elif current_day == 1:
            self._cancel_and_delete_orders(to_date)

    def _cancel_and_delete_orders(self, to_date):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: cancel and delete sale order as per the cofiguration
        """
        # TODO: When pre order will be install need to exclude pre-sale type orders
        order_ids = self.env['sale.order'].sudo().search([('state', '=', 'draft'), ('create_date', '<', to_date)],
                                                         limit=500)

        for order in order_ids:
            order.sudo().action_cancel()
            order.sudo().unlink()

    @api.model
    def order_by_saleorder_without_delivery_date(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: Dashboard Logistics report values are preparation
        """
        record_ids = []
        view_id_tree = self.env.ref('sale_marvelsa.dashboard_traffic_tree_view')
        view_id_form = self.env.ref('sale.view_order_form')
        customer_location = self.env.ref('stock.stock_location_customers')

        query = """
		select distinct sp.sale_id 
		from stock_picking sp inner join sale_order so 
			on so.id = sp.sale_id inner join  stock_picking_type spt 
			on spt.id = sp.picking_type_id
		where sp.state in ('assigned','done') and sp.x_studio_fecha_de_envio is null 
		and spt.code = 'outgoing' and so.date_order > '2021-02-01 01:00:00'
		and so.mostrador = false and sp.location_id != {0}
		""".format(customer_location.id)

        self.env.cr.execute(query)
        for row in self.env.cr.dictfetchall():
            record_ids.append(row['sale_id'])

        return {
            'type': 'ir.actions.act_window',
            'name': _('Dashboard Logistics'),
            'res_model': 'sale.order',
            'views': [(view_id_tree.id, 'list'), (view_id_form.id, 'form')],
            'view_mode': 'list, form',
            'target': 'current',
            'context': {'create': False},
            'domain': [('id', 'in', record_ids)]
        }

    def action_view_delivery_without_refund(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: open a picking view as per sale orders
        """
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        customer_location = self.env.ref('stock.stock_location_customers')

        pickings = self.mapped('picking_ids')
        # pickings = pickings.filtered(lambda p: p.location_id.id != customer_location.id)
        picking_ids = []
        for pick in pickings:
            if pick.location_id.id != customer_location.id:
                picking_ids.append(pick.id)

        if len(pickings) > 1:
            action['domain'] = [('id', 'in', picking_ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        return action

    def auto_confirm_sale_orders(self):
        """
            Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
            Purpose: confirm a sale order if delivery auto is true and order is created from website
        """
        message = "<h1>&#x1f44d; </h1><b><h3>Liberado en automatico.</h3></b>"
        sale_orders = self.env['sale.order'].sudo().search(
            [('delivery_auto', '=', True), ('state', '=', 'sent'), ('website_id', '!=',False)])

        for order in sale_orders:
            order.action_confirm()
            order.message_post(body=message)

    def get_payment_way(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: set Payment Way and details when confirm the order from website.
        """
        team = self.env['crm.team'].search([('name', '=', 'ML')])
        if self.team_id.id != team.id:
            if self.pricelist_id and self.pricelist_id.is_credit:
                payment_way = self.env['l10n_mx_edi.payment.method'].search(
                    [('name', '=', 'Por definir'), ('code', '=', '99')])
                self.l10n_mx_edi_payment_method_id = payment_way.id
            else:
                payment_transaction_id = self.env['payment.transaction'].search([('sale_order_ids','=',self.id)],order= 'create_date desc',limit=1)
                provider_id = False
                if payment_transaction_id:
                    provider_id = payment_transaction_id.provider_id

                if provider_id and not provider_id.code == 'bbva':
                    payment_way_id =  provider_id.l10n_mx_edi_payment_method_id
                    if not payment_way_id:
                        payment_way_id = self.partner_id.l10n_mx_edi_payment_method_id
                    if payment_way_id:
                        self.l10n_mx_edi_payment_method_id = payment_way_id

        if self.partner_id and self.partner_id.l10n_mx_edi_usage:
            self.l10n_mx_edi_usage = self.partner_id.l10n_mx_edi_usage

    def _prepare_order_line_values(self, product_id, quantity, linked_line_id=False, no_variant_attribute_value_ids=None,
                                   product_custom_attribute_values=None, combo_item_id=None, **kwargs):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: set is_oversized as per sale_order_line
        """
        vals = super()._prepare_order_line_values(product_id, quantity, linked_line_id,
                                                  no_variant_attribute_value_ids,
                                                  product_custom_attribute_values, combo_item_id, **kwargs)
        product = self.env['product.product'].browse(product_id)
        vals['is_oversized'] = product.is_oversized
        return vals


    @api.onchange('partner_id','pricelist_id')
    def onchange_payment_term_id(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: set the payment_term_id as per the pricelist configuration
        """
        if self.pricelist_id.payment_term_for_priceslist_id:
            self.payment_term_id = self.pricelist_id.payment_term_for_priceslist_id
        else:
            if self.partner_id.property_payment_term_id:
                self.payment_term_id = self.partner_id.property_payment_term_id

    def create(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: set the client_order_ref as per the partners city_id name
        """
        res = super(SaleOrder, self).create(vals)
        for order in res:
            if order._context.get('website_id'):
                if order.partner_shipping_id and order.partner_shipping_id.city_id:
                    order.client_order_ref = order.partner_shipping_id.city_id.display_name
        return res

    def write(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: set the client_order_ref as per the partners city_id name
        """
        shipping_partner = vals.get('partner_shipping_id', False)
        if shipping_partner:
            for order in self:
                if order._context.get('website_id'):
                    customer = order.env['res.partner'].browse(shipping_partner)
                    vals.update({'client_order_ref': customer.city_id.display_name or ""})
        return super(SaleOrder, self).write(vals)

    @api.constrains("partner_id","pricelist_id", "l10n_mx_edi_payment_method_id")
    def check_payment_way(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: set Payment Way and add constrain if condition not satisfied.
        """
        team = self.env['crm.team'].search([('name', '=', 'ML')])
        for rec in self:
            if rec.team_id.id != team.id and rec.pricelist_id and not rec.amazon_order_ref:
                if rec.pricelist_id.is_credit and rec.l10n_mx_edi_payment_method_id.code != '99':
                    payment_way = self.env['l10n_mx_edi.payment.method'].search(
                        [('name', '=', 'Por definir'), ('code', '=', '99')])
                    rec.l10n_mx_edi_payment_method_id = payment_way.id
                elif not rec.pricelist_id.is_credit and not rec.website_id and rec.l10n_mx_edi_payment_method_id.code == '99' and not rec.multi_ecommerce_connector_id and not rec.meli_orders:
                    raise UserError(
                        'No puede elegir una forma de pago como "Por definir" si es un pago de contado. ¡¡¡Defina un metodo de pago!!! o elija una lista de precios a credito.')

    @api.onchange('partner_id')
    def _onchange_usage_and_method(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 27/02/25
            Task: CFDI and payment Way Migration v16 to v18
            Purpose: set a l10n_mx_edi_payment_method_id and l10n_mx_edi_usage as per the conditions
            note : add this method here instead of CFDI and payment Way.
        """
        if self.partner_id:
            team = self.env['crm.team'].search([('name', '=', 'ML')])
            if self.team_id.id != team.id:
                if self.pricelist_id and self.pricelist_id.is_credit:
                    payment_way = self.env['l10n_mx_edi.payment.method'].search(
                        [('name', '=', 'Por definir'), ('code', '=', '99')])
                    self.l10n_mx_edi_payment_method_id = payment_way.id
                else:
                    payment_way_id = self.partner_id.l10n_mx_edi_payment_method_id.id
                    if payment_way_id:
                        self.l10n_mx_edi_payment_method_id = payment_way_id
        if self.partner_id and self.partner_id.l10n_mx_edi_usage:
            self.l10n_mx_edi_usage = self.partner_id.l10n_mx_edi_usage