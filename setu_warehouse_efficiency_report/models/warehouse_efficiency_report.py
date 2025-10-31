# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class WarehouseEfficiencyReport(models.Model):
    _name = "warehouse.efficiency.report"
    _description = "Warehouse Efficiency Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Many2one('stock.picking', string='Order Reference', readonly=True)
    total_time_difference = fields.Char(string="Total Time", readonly=True)
    picking_reference = fields.Char(string="Picking reference")

    picking_total_lines = fields.Integer(string="Picking total lines")

    product_uom_qty = fields.Float('Qty Ordered', readonly=True)
    qty_delivered = fields.Float('Qty Delivered', readonly=True)
    unsupplied_qty = fields.Float(string="Unsupplied Qty")

    date = fields.Datetime(string='Order Date', readonly=True)
    picking_scheduled_date = fields.Datetime(string='Assortment Start Date', readonly=True)
    picking_done_date = fields.Datetime(string="Picking End Date", readonly=True)

    product_type = fields.Selection(
        [('1', 'Producto Terminado'), ('2', 'Accesorio'), ('3', 'Refaccion'), ('4', 'Refaccion de Servicio')],
        readonly=True)

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Assortment Warehouse', readonly=True)
    warehouse_sugerido_id = fields.Many2one('stock.warehouse', string='suggested Warehouse', readonly=True)

    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    picking_id = fields.Many2one('stock.picking', string='Picking', readonly=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', readonly=True)
    owner_id = fields.Many2one('res.partner', string="Owner", readonly=True)
    percentage_efficiency_assortment = fields.Float('% efficiency assortment')
    source_location_id = fields.Many2one('stock.location', string='Source Location')
    destination_location_id = fields.Many2one('stock.location', string='Destination Location')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 10/03/25
            Task: Migration to v18 from v16
            Purpose: called the query for preparing the report during init execution.
        """
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
           row_number() over(order by mv.product_id) as id,
            tmpl.product_type_marvelsa as product_type,
            --False as product_type,

            mv.product_id as product_id,
             (mv.intial_order_quantity - mv.product_uom_qty)  as unsupplied_qty,
    		mv.intial_order_quantity  as product_uom_qty,
             mv.product_uom_qty  as qty_delivered,

            partner.warehouse_sugerido_id as warehouse_sugerido_id,

            s.partner_id as partner_id,
            s.name as name,
            pickty.warehouse_id as warehouse_id,

            s.date_order as date,
            s.state as state,
            s.id as order_id,

            pickty.id as picking_type_id,
            0 as percentage_efficiency_assortment,

            pick.id as picking_id,
            pick.scheduled_date as picking_scheduled_date,
            pick.date_done as picking_done_date,
            pick.date_done - pick.scheduled_date as total_time_difference,
            pick.name as picking_reference,
            count(mv.picking_id) as picking_total_lines,
            pick.owner_id as owner_id,
            pick.location_id as source_location_id,
    		pick.location_dest_id as destination_location_id

        """

        for field in fields.values():
            select_ += field

        from_ = """
                 stock_move mv
                      join stock_picking pick on (mv.picking_id=pick.id)
                      join sale_order s on pick.sale_id = s.id
                      join stock_picking_type pickty on pick.picking_type_id = pickty.id
                      join res_partner partner on s.partner_id = partner.id
                      join product_product p on mv.product_id=p.id
                      join product_template tmpl on p.product_tmpl_id=tmpl.id
                      join stock_warehouse sw on s.warehouse_id = sw.id
                      join sale_order_line l on mv.sale_line_id=l.id
                %s
        """ % from_clause

        groupby_ = """
            mv.product_id,
            l.order_id,
            l.product_uom_qty,
            mv.product_uom_qty,
            tmpl.product_type_marvelsa,
            pick.id,
            pick.date_done,
            pick.scheduled_date,
            pickty.id,
            partner.warehouse_sugerido_id,
            s.name,
            s.date_order,
            s.partner_id,
            s.warehouse_id,
            s.id,
            pick.location_id,pick.location_dest_id,mv.intial_order_quantity,mv.state %s """ % (groupby)

        return """%s (SELECT %s FROM %s  where s.state in ('sale') and  mv.state = 'done' 
         and pick.state = 'done' and pickty.code='outgoing' and mv.state != 'cancel' GROUP BY %s)""" % (
            with_, select_, from_, groupby_)

    def init(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 10/03/25
            Task: Migration to v18 from v16
            Purpose: prepared the report during called the init.
        """
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 10/03/25
            Task: Migration to v18 from v16
            Purpose: called read_group for the fields available in the report to adding domain and other things.
        """
        res = super().read_group(domain, fields, groupby, offset=offset, limit=limit,
                                 orderby=orderby, lazy=lazy)
        for dic in res:
            _domain = dic.get('__domain', False)
            if _domain and len(_domain) == 1:
                for dic in res:
                    for key, value in dic.items():
                        if '_count' in key.lower():
                            count = value
                            if 'percentage_efficiency_assortment' in dic.keys():
                                dic.update({'percentage_efficiency_assortment': (count / count)})
            if _domain and len(_domain) > 1:
                sum = 0
                for dic in res:
                    for key, value in dic.items():
                        if '_count' in key.lower():
                            sum += value
                for dic in res:
                    for key, value in dic.items():
                        if '_count' in key.lower():
                            percentage = (value / sum)
                            if 'percentage_efficiency_assortment' in dic.keys():
                                dic.update({'percentage_efficiency_assortment': percentage})
        return res
