# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    portal = fields.Char(string='Pedido Portal', size=15)
    mostrador = fields.Boolean(default=False, string='Cliente Mostrador', )
    dfactura = fields.Boolean(default=False, string='Detener Factura', )
    warehouse_sugerido_id = fields.Many2one('stock.warehouse', string="Surtido Sugerido",
                                            help="Almacen sugerido del cual se ba a surtir el "
                                                 "pedido del cliente",
                                            compute='_compute_warehouse_id', store=True, precompute=True)
    is_mark_done = fields.Boolean("Mark Done", default=False)

    @api.depends('user_id', 'company_id', 'partner_shipping_id')
    def _compute_warehouse_id(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 31/12/24
            Task: Migration from V16 to V18
            Purpose: set a warehouse on a sale order as per set in customer
        """
        _logger.debug("Compute _get_warehouse_sugerido_id method start")
        for rec in self:
            if not rec.partner_id:
                return super()._compute_warehouse_id()
            rec.warehouse_id = rec.partner_shipping_id.warehouse_sugerido_id.id or rec.partner_id.warehouse_sugerido_id.id or rec.warehouse_id.id
            rec.warehouse_sugerido_id = rec.partner_shipping_id.warehouse_sugerido_id.id or rec.partner_id.warehouse_sugerido_id.id or rec.warehouse_id.id
            if not rec.warehouse_id and hasattr(rec, 'amazon_channel') and rec.amazon_channel == "fbm": # this change is for amazon orders
                rec.warehouse_id = self.env['amazon.account'].search([], limit=1).location_id.warehouse_id.id
        _logger.debug("Compute _get_warehouse_sugerido_id method end")

    def _prepare_invoice(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 31/12/24
            Task: Migration from V16 to V18
            Purpose: set dfactura_invoice as per the sale order
        """
        res = super(SaleOrder, self)._prepare_invoice()
        if self.dfactura:
            res.update({'dfactura_invoice': True})
        if self.mostrador:
            res.update({'mostrador': True})
        return res

    def _set_delivery_method(self, *args, **kwargs):
        """
            Author: jay.garach@setuconsulting.com
            Date: 31/12/24
            Task: Migration from V16 to V18 (https://app.clickup.com/t/865d9qqqu)
            Purpose: Set a mostrador as per the shipping method configuration.
        """
        res = super()._set_delivery_method(*args, **kwargs)
        if self.carrier_id.is_mostrador_delivery:
            self.mostrador = True
        else:
            self.mostrador = False
        return res
