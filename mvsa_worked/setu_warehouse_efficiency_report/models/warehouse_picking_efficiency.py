from odoo import api, fields, models
from odoo import tools


class WarehousePickingEfficiency(models.Model):
    _name = 'warehouse.picking.efficiency.report'
    _description = 'WarehousePickingEfficiencyReport'
    _auto = False
    _rec_name = 'picking_reference'
    _check_company_auto = True

    picking_reference = fields.Many2one("stock.picking", string="Picking reference")
    picking_total_lines = fields.Integer(string="Picking total lines")
    warehouse_id = fields.Char(string='Assortment Warehouse', readonly=True)
    product_type = fields.Selection([('1', 'Producto Terminado'), ('2', 'Accesorio'), ('3', 'Refaccion'),
                                     ('4', 'Refaccion de Servicio')])
    picking_product_uom_qty = fields.Float(string="Qty Ordered Total")
    picking_qty_delivered = fields.Integer(string="Qty Delivered Total")
    picking_scheduled_date = fields.Datetime(string='Assortment Start Date', readonly=True)
    picking_done_date = fields.Datetime(string="Picking End Date", readonly=True)
    total_time_difference = fields.Char(string="Total Time", readonly=True)
    owner = fields.Char(string="Owner")
    responsible_person_id = fields.Many2one('hr.employee', string="Responsible Person")

    def init(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 10/03/25
            Task: Migration to v18 from v16
            Purpose: prepared the report during called the init.
        """
        tools.drop_view_if_exists(self.env.cr, 'warehouse_picking_efficiency_report')
        self.env.cr.execute("""
                CREATE or REPLACE VIEW warehouse_picking_efficiency_report AS(
                select 
                        row_number() over(order by sp.id) AS id,
                
                        sp.id as picking_reference, 
	                    count(sp.name) as picking_total_lines, 
	                    sw.name as warehouse_id,
	                    sp.responsible_person as responsible_person_id,
	                    
	                    pt.product_type_marvelsa as product_type,
	                    --False as product_type,
	                    sum(sm.product_uom_qty) as picking_product_uom_qty,
	                    sum(sml.quantity) as picking_qty_delivered,
	                    sp.scheduled_date as picking_scheduled_date,
	                    sp.date_done as picking_done_date,
	                    sp.date_done - sp.scheduled_date as total_time_difference,
	                    rp.name as owner
		            from stock_picking sp 
		                join stock_move sm on (sp.id=sm.picking_id)
		                join stock_picking_type spt on (sp.picking_type_id=spt.id)
		                
		                join stock_move_line sml on(sm.id = sml.move_id)
		                join product_product pp on(sml.product_id = pp.id)
		                join product_template pt on(pp.product_tmpl_id = pt.id)
		                
		                Left join stock_warehouse sw on (spt.warehouse_id=sw.id)
		                Left join res_partner rp on(sp.owner_id=rp.id)
		            where sp.state='done'
		            group by sp.id,
		                    pt.product_type_marvelsa,
		                    sp.scheduled_date,
		                    sp.date_done,
		                    sw.name,
		                    rp.name,
		                    sp.responsible_person
		                    
                )""")
