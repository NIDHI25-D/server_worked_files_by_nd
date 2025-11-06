# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class PosResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    wk_display_stock = fields.Boolean(related='pos_config_id.wk_display_stock', readonly=False)
    wk_stock_type = fields.Selection(related='pos_config_id.wk_stock_type', readonly=False)
    wk_continous_sale = fields.Boolean(related='pos_config_id.wk_continous_sale', readonly=False)
    wk_deny_val = fields.Integer(related='pos_config_id.wk_deny_val', readonly=False)
    wk_error_msg = fields.Char(related='pos_config_id.wk_error_msg', readonly=False)
    wk_hide_out_of_stock = fields.Boolean(related='pos_config_id.wk_hide_out_of_stock', readonly=False)

    @api.model
    def wk_pos_fetch_pos_stock(self, kwargs):
        result = {}
        location_id = False
        wk_stock_type = kwargs['wk_stock_type']
        wk_hide_out_of_stock = kwargs['wk_hide_out_of_stock']
        config_id = self.env['pos.config'].browse([kwargs.get('config_id')])
        picking_type = config_id.picking_type_id
        location_id = picking_type.default_location_src_id.id
        product_obj = self.env['product.product']
        pos_products = product_obj.search([('sale_ok', '=', True), ('available_in_pos', '=', True)])
        pos_products_qtys = pos_products.with_context(location=location_id)._compute_quantities_dict(lot_id=None,
                                                                                                     owner_id=None,
                                                                                                     package_id=None)
        for pos_product in pos_products_qtys:
            if wk_stock_type == 'available_qty':
                if wk_hide_out_of_stock and pos_products_qtys[pos_product]['qty_available'] > 0:
                    result[pos_product] = pos_products_qtys[
                        pos_product]['qty_available']
                if not wk_hide_out_of_stock:
                    result[pos_product] = pos_products_qtys[
                        pos_product]['qty_available']
            elif wk_stock_type == 'forecasted_qty':
                if wk_hide_out_of_stock and pos_products_qtys[pos_product]['virtual_available'] > 0:
                    result[pos_product] = pos_products_qtys[
                        pos_product]['virtual_available']
                if not wk_hide_out_of_stock:
                    result[pos_product] = pos_products_qtys[
                        pos_product]['virtual_available']
            else:
                if wk_hide_out_of_stock and pos_products_qtys[pos_product]['qty_available'] - \
                        pos_products_qtys[pos_product]['outgoing_qty'] > 0:
                    result[pos_product] = pos_products_qtys[pos_product][
                                              'qty_available'] - pos_products_qtys[pos_product]['outgoing_qty']
                if not wk_hide_out_of_stock:
                    result[pos_product] = pos_products_qtys[pos_product][
                                              'qty_available'] - pos_products_qtys[pos_product]['outgoing_qty']
        return result
