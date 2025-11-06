from odoo import models
from odoo.http import request
from datetime import datetime, timedelta


class Website(models.Model):
    _inherit = "website"

    def _search_get_details(self, search_type, order, options):
        result = super()._search_get_details(search_type, order, options)
        if search_type in ['products_only'] and options.get('new_arrival'):
            day = int(request.env['ir.config_parameter'].sudo().get_param('new_arrival_products_menu.new_arrival_products_filter_days'))
            past = datetime.now() - timedelta(days=day)
            new_arrival_pro = request.env['stock.move'].sudo().search(
                [('location_id.usage', '=', 'supplier'), ('date', '>=', past), ('state', '=', 'done')]).mapped(
                'product_id.product_tmpl_id').filtered(lambda pro: (pro.qty_available - pro.outgoing_qty) >= 1).ids
            if not new_arrival_pro:
                context = request.env.context.copy()
                context.update({'no_newArrivals_products': True})
                request.update_context(**context)
                return result
            context = request.env.context.copy()
            context.update({'no_newArrivals_products': False})
            request.update_context(**context)
            domain = [('id', 'in', new_arrival_pro)]
            result[0]['base_domain'][0].extend(domain)
        return result
