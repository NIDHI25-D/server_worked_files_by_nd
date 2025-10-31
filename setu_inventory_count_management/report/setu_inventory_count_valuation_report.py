# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.addons.setu_inventory_count_management.report.const import get_dynamic_query

class InventoryCountValuationUpDownReport(models.TransientModel):
    _name = 'setu.inventory.count.valuation.report'
    _inherit = 'setu.inventory.reporting.template'
    _description = 'Inventory Count Valuation Up/Down Report'

    count_id = fields.Many2one(comodel_name="setu.stock.inventory.count", string="Count")
    lot_id = fields.Many2one(comodel_name="stock.lot", string="Lot")

    valuation_graph = fields.Selection([('UP', 'UP'), ('DOWN', 'DOWN')], string="Up/Down")

    adjusted_qty = fields.Float(string="Quantity")
    total_valuation = fields.Float(string="Valuation")

    company_id = fields.Many2one(comodel_name="res.company", string="Company")

    user_ids = fields.Many2many(comodel_name="res.users", string="Users"

                                )
    location_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Locations"
    )

    def generate_report(self):
        location_ids = False
        user_ids = False
        if self.location_ids:
            location_ids = 'ARRAY' + str(self.location_ids.ids)
        if self.user_ids:
            user_ids = 'ARRAY' + str(self.user_ids.ids)
        where_query = get_dynamic_query(
            'source.id', location_ids,
            'count.approver_id', user_ids,
            '', []
        )
        start_date = '1990-01-01'
        end_date = '2100-01-01'

        if self.start_date:
            start_date = str(self.start_date)
        if self.end_date:
            end_date = str(self.end_date)
        self._cr.execute('delete from setu_inventory_count_valuation_report;')
        query = f"""select 
                        sml.product_id,
                        sml.lot_id,
                        case when source.usage='internal' then -1 * sml.quantity else sml.quantity end as adjusted_qty,
                        svl.value as total_valuation,
                        case when source.usage='internal' then sml.location_id else sml.location_dest_id end as location_id,
                        count.id as count_id,
                        case when source.usage='internal' then 'DOWN' else 'UP' end as valuation_graph,
                        count.approver_id as user_id,
                        count.inventory_count_date as inventory_count_date,
                        svl.company_id 
                    from 
                        stock_valuation_layer svl 
                        join stock_move sm on sm.id = svl.stock_move_id
                        join stock_move_line sml on sml.move_id = sm.id 
                        join setu_stock_inventory_count count on count.id = sm.inventory_count_id
                        Join stock_location source on source.id = sml.location_id
                        Join stock_location dest on dest.id = sml.location_dest_id
                    where
                        count.inventory_count_date >= '{str(start_date)}' and count.inventory_count_date <= '{str(end_date)}'
                        {where_query};
        """
        self._cr.execute(query)
        data_list = self._cr.dictfetchall()
        for data in data_list:
            self.create({
                'product_id': data['product_id'],
                'company_id': data['company_id'],
                'lot_id': data['lot_id'],
                'location_id': data['location_id'],
                'inventory_count_date': data['inventory_count_date'],
                'adjusted_qty': data['adjusted_qty'],
                'total_valuation': data['total_valuation'],
                'user_id': data['user_id'],
                'count_id': data['count_id'],
                'valuation_graph': data['valuation_graph']
            })
        action = \
            self.sudo().env.ref('setu_inventory_count_management.setu_inventory_count_valuation_report_record_action').read()[0]
        return action
