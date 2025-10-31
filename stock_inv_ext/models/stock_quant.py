from odoo import fields, models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible', readonly=1,
        required=False, default=lambda self: self.env.user.id)

    manager_id = fields.Many2one(
        comodel_name='res.users',
        string='Manager', read=['stock.group_stock_manager'],
        help="select your manager who will be reviewing this inventory.")

    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", related="location_id.warehouse_id", store=True)


    # def get_barcode_view_state(self):
    #     res = super(StockQuant, self).get_barcode_view_state()
    #     if res:
    #         res[0]['group_stock_inventory_supervisor'] = self.env.user.has_group('stock_inv_ext.group_stock_inventory_supervisor')
    #     return res
