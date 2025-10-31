from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

UNIT = dp.get_precision('Product Unit of Measure')


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_get_quantity_warehouses_dict(self):
        """
            Authour: nidhi@setconsulting
            Date: 6/12/2024
            Task: Migration from V16 to V18
            Purpose: This method holds a query which gives the main warehouse with their priority.
                     Also, it gives content of warehouses presnet in the alternative warehouse with the main warehouse.
                     eg:[{'qty_available': 91.0, 'free_qty': 88.0, 'incoming_qty': 0.0, 'outgoing_qty': 3.0, 'virtual_available': 88.0,
                          'warehouse_id': 4, 'warehouse': 'Warehouse 3', 'warehouse_short': 'W3', 'product': 46}]
        """
        self.ensure_one()
        warehouse_ids = []
        info = {'content': []}
        query = ""
        # Just in case it's asked from other place different than product
        # itself, we enable this context management
        warehouse_id = self._context.get('warehouse_id')

        if warehouse_id:
            query = """
			SELECT  id warehouse_id, -1 as priority from stock_warehouse sw 
				where sw.id = {0}
				union all 
				select warehouse_to_picking_id warehouse_id, priority from alternative_warehouse 
				asw
			where asw.warehouse_id = {0}
			order by priority asc
			""".format(warehouse_id)
            self._cr.execute(query)

            for row in self._cr.dictfetchall():
                for warehouse in self.env['stock.warehouse'].sudo().browse(row['warehouse_id']):
                    product = self.sudo().with_context(warehouse=warehouse.id, location=False, multi_warehouse=True,
                                                       sale_order_multi=True, warehouse_id=warehouse.id)
                    quantity_dict = product._compute_quantities_dict(False, False, False).get(product.id)
                    quantity_dict.update({'warehouse_id': warehouse.id, 'warehouse': warehouse.name,
                                          'warehouse_short': warehouse.code, 'product': product.id})
                    info['content'].append(quantity_dict)
                    if warehouse_id and warehouse_id == warehouse.id:
                        info['warehouse'] = quantity_dict['free_qty']
        return info
