# -*- coding: utf-8 -*-
import datetime

from odoo import api, fields, models, _
import logging
from odoo.http import request
import pytz
from datetime import timedelta

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    available_for_preorder = fields.Boolean(string="Available for Pre-order",
                                            compute='_compute_available_for_preorder',
                                            default=False, store=True)

    available_for_presale = fields.Boolean(string="Available for Pre-Sale",
                                           compute='_compute_available_for_presale',
                                           default=False, store=True)

    presale_qty = fields.Float(string="Presale Qty", compute="_compute_available_for_presale", store=True)
    preorder_qty = fields.Float(string="Preorder Qty", compute="_compute_available_for_preorder", store=True)
    presale_price = fields.Float(string="Presale Price")
    presale_price_incl_tax = fields.Float(string="Presale Price Inc. Tax")
    calculated_qty = fields.Integer(string="Calulated Quantity")
    is_international_pre_order_product = fields.Boolean(string="Is International pre-order product",
                                                        compute="_compute_international_preorder", default=False,
                                                        store=True)
    international_preorder_qty = fields.Float(string="International Preorder Qty",
                                              compute="_compute_international_preorder", store=True)
    exclusive_partner_id = fields.Many2one("res.partner", string="Exclusive Partner")


    @api.depends('purchase_order_line_ids', 'purchase_order_line_ids.state', 'purchase_order_line_ids.product_qty',
                 'purchase_order_line_ids.pre_ordered_qty', 'purchase_order_line_ids.preorder_rel_ids',
                 'purchase_order_line_ids.preorder_rel_ids.preorder_qty',
                 'purchase_order_line_ids.preorder_rel_ids.pre_order_state', 'purchase_order_line_ids.move_ids.state')
    def _compute_available_for_preorder(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the Available for Pre-order and Preorder Qty from the dictionary are get from the method _get_product_availability, if product are preorder type else available_for_preorder are False and preorder_qty are 0.0. 
        """
        enable_pre_order = self.env['website'].sudo().get_current_website().enable_pre_order
        if bool(enable_pre_order):
            product_dict = self._get_product_availability("available_for_preorder")
            for product in self:
                if product in product_dict:
                    product.available_for_preorder = True
                    product.preorder_qty = product_dict[product]
                else:
                    product.preorder_qty = 0.0
                    product.available_for_preorder = False
        else:
            self.write({'preorder_qty': 0.0, 'available_for_preorder': False})

    @api.depends('purchase_order_line_ids', 'purchase_order_line_ids.state', 'purchase_order_line_ids.product_qty',
                 'purchase_order_line_ids.presale_rel_ids', 'purchase_order_line_ids.presale_rel_ids.presale_qty',
                 'purchase_order_line_ids.presale_rel_ids.pre_sale_state', 'purchase_order_line_ids.move_ids.state')
    def _compute_available_for_presale(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the Available for Pre-Sale and Presale Qty from the dictionary are get from the method _get_product_availability, if product are presale type else available_for_presale are False and presale_qty are 0.0. 
        """
        enable_pre_sale = self.env['website'].sudo().get_current_website().enable_pre_sale
        if bool(enable_pre_sale):
            product_dict = self._get_product_availability("available_for_presale")
            for product in self:
                if product in product_dict:
                    product.presale_qty = product_dict[product]
                    product.available_for_presale = True
                else:
                    product.presale_qty = 0.0
                    product.available_for_presale = False
                    product.presale_price = 0.0
                    product.presale_price_incl_tax = 0.0
        else:
            self.write({'presale_qty': 0.0, 'available_for_presale': False})

    @api.depends('purchase_order_line_ids', 'purchase_order_line_ids.state', 'purchase_order_line_ids.product_qty',
                 'purchase_order_line_ids.international_preorder_rel_ids',
                 'purchase_order_line_ids.international_preorder_rel_ids.international_preorder_qty',
                 'purchase_order_line_ids.international_preorder_rel_ids.international_pre_order_state',
                 'purchase_order_line_ids.move_ids.state')
    def _compute_international_preorder(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the Is International pre-order product and International Preorder Qty from the dictionary are get from the method _get_product_availability, if product are international preorder else is_international_pre_order_product are False and international_preorder_qty are 0.0.
        """
        product_dict = self._get_product_availability("is_international_pre_order_product")
        for product in self:
            if product in product_dict:
                product.international_preorder_qty = product_dict[product]
                product.is_international_pre_order_product = True
            else:
                product.international_preorder_qty = 0.0
                product.is_international_pre_order_product = False

    def _get_product_availability(self, product_type):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: prepared a dictionary for available_for_presale, available_for_preorder and is_international_pre_order_product as per the given parameters.
        """
        order_lines = self.preorder_presale_po_search(product_type)
        if product_type == "available_for_presale":
            qty_type = 'pre_sale_qty'
        elif product_type == "is_international_pre_order_product":
            qty_type = 'international_pre_order_qty'
        else:
            qty_type = "pre_ordered_qty"

        product_dict = {}
        for order_line in order_lines:
            if order_line.product_id in product_dict:
                product_dict[order_line.product_id] += order_line.product_uom_qty - order_line[qty_type]
            else:
                product_dict[order_line.product_id] = order_line.product_uom_qty - order_line[qty_type]
        return product_dict

    def preorder_presale_po_search(self, product_type):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: get order lines as per the conditions fulfilment. 
        """
        order_line_obj = self.env['purchase.order.line'].sudo()
        if product_type == "available_for_presale":
            domain = [('product_id', 'in', self.ids), ('state', 'in', ['purchase','done']),
                      ('order_id.is_presale_type', '!=', False), ('qty_received', '<', 1), ('product_qty', '>=', 1),
                      ('date_planned', '>', datetime.datetime.now().astimezone(pytz.timezone('America/Mexico_City')))]
        elif product_type == "available_for_preorder":
            domain = [('product_id', 'in', self.ids), ('state', 'in', ['draft']),
                      ('order_id.is_preorder_type', '!=', False),
                      ('date_planned', '>', datetime.datetime.now().astimezone(pytz.timezone('America/Mexico_City')))]
        else:
            domain = [('product_id', 'in', self.ids), ('state', 'in', ['draft']),
                      ('order_id.is_international_pre_order', '!=', False),
                      ('date_planned', '>', datetime.datetime.now().astimezone(pytz.timezone('America/Mexico_City')))]
        order_lines = order_line_obj.search(domain, order="date_planned,id asc")
        if product_type == "available_for_presale":
            order_lines.invalidate_recordset(fnames=['pre_sale_qty'])
            order_lines = order_lines.filtered(lambda x: (x.product_uom_qty - x.pre_sale_qty) > 0)
        elif product_type == "available_for_preorder":
            order_lines.invalidate_recordset(fnames=['pre_ordered_qty'])
            order_lines = order_lines.filtered(lambda x: (x.product_uom_qty - x.pre_ordered_qty) > 0)
        elif product_type == "is_international_pre_order_product":
            order_lines.invalidate_recordset(fnames=['international_pre_order_qty'])
            order_lines = order_lines.filtered(lambda x: (x.product_uom_qty - x.international_pre_order_qty) > 0)
        return order_lines

    def presale_product_price_update(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: Set a product presale-price as per granularity from scheduled action as well conditionality.
        """
        if self.env.context.get('po'):
            po = self.env.context.get('po').order_line.mapped('product_id').mapped('id')
            product_ids = self.search([('id','in',po),('available_for_presale', '=', True), ('import_factor_level_id', '!=', False),
                                       ('competition_level_id', '!=', False)])
        else:
            product_ids = self.search([('available_for_presale', '=', True), ('import_factor_level_id', '!=', False),
                                   ('competition_level_id', '!=', False)])
        run_as = 'From PO' if self.env.context.get('po') else 'From Cron'
        cash_payment = self.env['website'].sudo().get_current_website().cash_payment
        for product in product_ids:
            before_update_price = product.presale_price
            presale_incoming = self.env['purchase.order.line'].search(
                domain=[('product_id', 'in', product.ids), ('state', 'in', ['purchase','done']),
                        ('order_id.is_presale_type', '!=', False), ('qty_received', '<', 1), ('product_qty', '>=', 1),
                        (
                            'date_planned', '>',
                            datetime.datetime.now().astimezone(pytz.timezone('America/Mexico_City')))],
                order="date_planned,id asc").filtered(lambda x: x.product_qty != x.pre_sale_qty).read(
                fields=['date_planned', 'price_unit', 'currency_id', 'date_approve'])
            if presale_incoming and product.competition_level_id.price_base_ids:
                date_planned_mx = presale_incoming[0].get('date_planned').astimezone(
                    pytz.timezone('America/Mexico_City')).date()
                presale_start_date = presale_incoming[0].get('date_approve').astimezone(
                    pytz.timezone('America/Mexico_City')).date()
                diff = (date_planned_mx - datetime.datetime.now().astimezone(
                    pytz.timezone('America/Mexico_City')).date()).days
                if presale_incoming[0].get('currency_id')[0] != self.env.company.currency_id.id:
                    presale_exchange_rate = self.env['website'].sudo().get_current_website().presale_exchange_rate
                else:
                    presale_exchange_rate = 1

                if diff > 0:
                    price_base = product.competition_level_id.price_base_ids.filtered(
                        lambda x: x.day_start < diff <= x.day_end)
                    prev_price_base = product.competition_level_id.price_base_ids.filtered(
                        lambda x: x.day_end <= price_base.day_start)
                    prev_granulaties = 0
                    for base in prev_price_base:
                        prev_granulaties += (base.day_end - base.day_start)

                    # Days that need to be granulated  [ DTG ]
                    days_to_granulate = (price_base.day_end - price_base.day_start)
                    # Remaining Days to the Range end Date [ RDTG ]
                    remailning_days_to_end_date = diff - prev_granulaties
                    # Margin to Granulate [ MTG ]
                    if prev_price_base:
                        granularity_margin = prev_price_base[-1].discount - price_base.discount
                    else:
                        granularity_margin = product.competition_level_id.final_profit_margin - price_base.discount
                    # Ganulate by Day [ DG ]
                    granularity_by_day = granularity_margin / days_to_granulate if days_to_granulate != 0.0 else 0.0
                    elapsed_days = days_to_granulate - remailning_days_to_end_date
                    price = presale_incoming[0].get('price_unit')
                    presale_price = ((price * product.import_factor_level_id.import_factor * presale_exchange_rate)) / (
                            (100 - (price_base.discount + (elapsed_days * granularity_by_day))) / 100)
                    presale_price = presale_price / cash_payment
                    res = product.taxes_id.compute_all(presale_price, product=product, partner=self.env['res.partner'])
                    product.presale_price = presale_price
                    product.presale_price_incl_tax = res['total_included']
                    _logger.info(
                        "price %s import factor %s exchange rate %s discount %s elapsed day %s granularity by day %s ",
                        price,
                        product.import_factor_level_id.import_factor, presale_exchange_rate,
                        price_base.discount, elapsed_days, granularity_by_day)
                else:
                    _logger.info("Product %s difference is Zero", product.name)
            else:
                product.presale_price = product.list_price

            _logger.info("Product %s %s to %s Executed %s", product.name, before_update_price, product.presale_price,
                         run_as)
        if self.env['ir.module.module'].sudo().search([('name', '=', 'queue_job'), ('state', '=', 'installed')],
                                                      limit=1):
            self.with_delay().sale_order_price_and_promotions_update()

    def sale_order_price_and_promotions_update(self): # after queue job.
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 28/04/25
            Task: Migration to v18 from v16
            Purpose: update non confirmed sale orders via queue job.
        """
        _logger.info("sale order price update is start")
        sale_order_ids = self.env['sale.order'].search(
            [('is_presale', '=', True), ('state', '=', 'draft'), ('transaction_ids', '=', False)])
        _logger.info("sale orders====>%s", sale_order_ids)
        sale_order_lines = sale_order_ids.order_line
        for line in sale_order_lines:
            line._compute_price_unit()
        _logger.info("sale order price update is end")
        _logger.info("sale order discount and loyalty is start")
        for order in sale_order_ids:
            _logger.info("sale order %s is started", order.name)
            try:
                order._update_programs_and_rewards()
                order._auto_apply_rewards()
                _logger.info("sale order %s is finished", order.name)
            except Exception as e:
                _logger.info(f"Error occurs during the update promotions on sale orders :- {e},{order.name})")
                order.message_post(body=e)
        _logger.info("sale order discount and loyalty is end")


    def apply_calculate_available_website_quantities(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: calculate/update Calulated Quantity via scheduled action.
        """
        website_data = self.env['website'].get_current_website()
        days_for_calculation = website_data.days_for_calculation
        configure_date = datetime.datetime.now() - timedelta(days=days_for_calculation)
        query = """
                With website_table as (
                    SELECT web.stock_pick_type as stock_pick_type,
                           web.available_qty_multiplier as available_qty_multiplier,
                           web.minimum_amt_qty as minimum_amt_qty
                    FROM website web
                ),
                free_qty as (
                    SELECT
                      sq.product_id as product_id,
                    SUM(sq.quantity - sq.reserved_quantity) AS "quantity"
                FROM
                    public.stock_quant sq
                LEFT JOIN public.stock_location sl ON sq.location_id = sl.id
                RIGHT JOIN public.product_product pp ON pp.id = sq.product_id
                WHERE 1 = CASE
                            WHEN (SELECT stock_pick_type FROM website_table WHERE stock_pick_type = 'Several') = 'Several'
                                AND sq.location_id IN (
                                        SELECT sl.id
                                        FROM public.website web
                                        LEFT JOIN public.website_sale_warehouse_rel wswr ON wswr.website_id = web.id
                                        LEFT JOIN public.stock_warehouse sw ON sw.id = wswr.stock_warehouse_id
                                        LEFT JOIN public.stock_location sl ON sl.warehouse_id = sw.id
                                        WHERE  sl.usage='internal'
                                        GROUP BY sl.id
                                    ) THEN 1
                            WHEN (SELECT stock_pick_type FROM website_table WHERE stock_pick_type = 'Specific') = 'Specific' AND
                                sq.location_id IN (
                                    SELECT sl.id
                                    FROM website web
                                    LEFT JOIN public.stock_warehouse sw ON sw.id = web.warehouse_default_id
                                    LEFT JOIN public.stock_location sl ON sl.warehouse_id = sw.id
                                    WHERE  sl.usage='internal'
                                ) THEN 1
                            WHEN (SELECT stock_pick_type FROM website_table WHERE stock_pick_type = 'All') = 'All'
                            AND sq.location_id IN (
                                    select sl.id from public.stock_location sl
                                where  sl.usage='internal'
                            )
                            THEN 1
                        END
                -- and sq.product_id =111938
                -- AND  sq.product_id IN %s
                GROUP BY
                    sq.product_id
                ),

                 product_calculations AS 
                 (
                    SELECT product_id,max(max_product_uom_qty) as max_product_uom_qty from 
                    (
                            SELECT	sol.product_id,
                                MAX(sol.product_uom_qty) AS max_product_uom_qty
                                FROM sale_order so
                                LEFT JOIN sale_order_line sol ON so.id = sol.order_id
                                LEFT JOIN product_product pp ON sol.product_id = pp.id
                                WHERE
                                    so.state in ('sale')
                                    AND so.date_order > '{}'
                                    AND pp.active = 't'
                                GROUP BY
                                    sol.product_id
				        UNION 
                             SELECT
                                    pp.id AS product_id,
                                    0 AS max_product_uom_qty
                                FROM
                                    product_product pp
                                WHERE
                                    pp.active = 't' 
                                GROUP BY pp.id 
                   ) products 
                    group by product_id
                )
                -- UPDATE  calculated_qty
                UPDATE product_product
                SET calculated_qty =
                    CASE
                        WHEN (max_product_uom_qty * available_qty_multiplier) < minimum_amt_qty AND fq.quantity > minimum_amt_qty
                             THEN minimum_amt_qty
                        ELSE CASE WHEN  (max_product_uom_qty * available_qty_multiplier) > minimum_amt_qty
                                        AND (max_product_uom_qty * available_qty_multiplier) < fq.quantity
                                        THEN (max_product_uom_qty * available_qty_multiplier)
                        ELSE CASE WHEN fq.quantity < minimum_amt_qty OR fq.quantity <  (max_product_uom_qty * available_qty_multiplier)
                             THEN fq.quantity
                        ELSE CASE WHEN minimum_amt_qty < fq.quantity then minimum_amt_qty 
						ELSE fq.quantity
                            END
                        END
                    END
                END
                FROM product_calculations pc
                LEFT JOIN free_qty fq on fq.product_id = pc.product_id
                CROSS JOIN website_table wt
                WHERE product_product.id = pc.product_id
        """.format(configure_date.date())
        self._cr.execute(query)

    def _is_add_to_cart_allowed(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16 --> Website - enhancement { https://app.clickup.com/t/86dtwa8bt }
            Purpose: As per the condition : Only storable type products should be added. It will not show order again if there is only 1 product and that too not of product_type in sale_order
        """
        res = super()._is_add_to_cart_allowed()
        if self.is_storable:
            return res
        else:
            return False