# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.http import request
import logging
import datetime
import pytz

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    available_for_preorder = fields.Boolean(string="Available for Pre-order",
                                            default=False, store=True,
                                            compute='_compute_available_for_preorder')
    is_preorder_type = fields.Boolean(string="Type of Pre-Order?",
                                      copy=False,
                                      help="Enabled the field to display the product as pre-order "
                                           "once it is "
                                           "below the specified minimum quantity.")

    available_for_presale = fields.Boolean(string="Available for Pre-Sale",
                                           default=False, store=True,
                                           compute='_compute_available_for_presale')
    is_presale_type = fields.Boolean(string="Type of Pre-Sale?",
                                     copy=False,
                                     help="Enabled the field to display the product as pre-Sale "
                                          "once it is "
                                          "below the specified minimum quantity.")

    preorder_minimum_qty = fields.Float(string="Minimum Pre-order/Pre-sale Quantity", copy=False)
    preorder_note = fields.Char(string="Pre-order/Pre-sale Note")
    is_international_pre_order_product = fields.Boolean(string="Is International pre-order product",default=False, store=True,compute="_compute_is_international_preroder")
    exclusive_partner_id = fields.Many2one("res.partner", string="Exclusive Partner", store=True,compute="_compute_is_international_preroder")
    minimum_exclusivity_quantity = fields.Integer(string="Minimum Exclusivity Quantity", copy=False)
    delivery_estimated_time = fields.Integer(string="Delivery Estimated Time",copy=False)
    next_day_shipping = fields.Boolean('Next Day Shipping')

    def _website_show_quick_add(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 15/07/25
            Task: Migration to v18 from v16
            Purpose: give feasibility to add to cart at list in website when selecting a product also, manage instock, presale and preorder scenario.
        """
        return True


    @api.depends('product_variant_ids.available_for_preorder','product_variant_ids.exclusive_partner_id')
    def _compute_available_for_preorder(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the Available for Pre-order from the variant.
        """
        for product in self:
            product.available_for_preorder = False
            for variant in product.product_variant_ids:
                if variant.available_for_preorder:
                    product.available_for_preorder = True
                    break

    @api.depends('product_variant_ids.available_for_presale')
    def _compute_available_for_presale(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the Available for Pre-Sale from the variant.
        """
        for product in self:
            product.available_for_presale = False
            for variant in product.product_variant_ids:
                if variant.available_for_presale:
                    product.available_for_presale = True
                    break

    @api.depends('product_variant_ids.is_international_pre_order_product','product_variant_ids.exclusive_partner_id')
    def _compute_is_international_preroder(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the Is International pre-order product and Exclusive Partner from the variant.
        """
        for product in self:
            product.is_international_pre_order_product = False
            product.exclusive_partner_id = False
            for variant in product.product_variant_ids:
                if variant.is_international_pre_order_product:
                    product.is_international_pre_order_product = True
                    if variant.exclusive_partner_id:
                        product.exclusive_partner_id = variant.exclusive_partner_id
                        break
                    break

    def _get_combination_info(
            self, combination=False, product_id=False, add_qty=1.0,
            parent_combination=False, only_template=False,
        ):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 15/04/25
            Task: Migration to v18 from v16 --> Website - enhancement { https://app.clickup.com/t/86dtwa8bt }
            Purpose: This method is used to update the free_qty of product when the Pop-up of Order again is opened.
            The main purpose of this method is to take free_qty of the product as the warehouse mentioned in the Settings.
        """
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty,
            parent_combination=parent_combination, only_template=only_template)
        presale_qty = 0.0
        order_line_obj = self.env['purchase.order.line'].sudo()
        product = self.env['product.product'].sudo().browse(combination_info['product_id'])
        order_lines = order_line_obj.search([('product_id', '=', product.id), ('state', 'in', ['purchase', 'done']),
                                             ('order_id.is_presale_type', '!=', False), ('qty_received', '<', 1),
                                             ('product_qty', '>=', 1),
                                             ('date_planned', '>', datetime.datetime.now().astimezone(
                                                 pytz.timezone('America/Mexico_City')))],
                order="date_planned asc").filtered(lambda x: (x.product_uom_qty - x.pre_sale_qty) > 0)
        if order_lines:
            order_line = order_lines[0]
            presale_qty += order_line.product_uom_qty - order_line.pre_sale_qty

        website = self.env['website'].get_current_website()
        combination_info.update(
            {'free_qty': product.with_context(warehouse_id=website._get_website_location_type()).free_qty, 'presale_qty': presale_qty})
        return combination_info
