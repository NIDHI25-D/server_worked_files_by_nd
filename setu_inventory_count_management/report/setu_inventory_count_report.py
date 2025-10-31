# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.addons.setu_inventory_count_management.report.const import get_dynamic_query


class SetuInvCountReport(models.TransientModel):
    _name = 'setu.inventory.count.report'
    _inherit = 'setu.inventory.reporting.template'
    _description = 'Inventory Count Report'

    count_id = fields.Many2one(
        comodel_name="setu.stock.inventory.count",
        string="Count"
    )
    users_ids = fields.Many2many("res.users", "inv_count_report_user_rel", "inv_count_report_id", "users_id",
                                 string="Users", compute="_compute_users_ids")

    @api.depends('user_ids')
    def _compute_users_ids(self):
        for record in self:
            users = self.sudo().env.ref(
                'setu_inventory_count_management.group_setu_inventory_count_manager').users
            record.users_ids = users if users else False

    def generate_report(self):
        location_ids = False
        warehouse_ids = False
        user_ids = False
        if self.location_ids:
            location_ids = 'ARRAY' + str(self.location_ids.ids)
        if self.warehouse_ids:
            warehouse_ids = 'ARRAY' + str(self.warehouse_ids.ids)
        if self.user_ids:
            user_ids = 'ARRAY' + str(self.user_ids.ids)
        where_query = get_dynamic_query(
            'count_line.location_id', location_ids,
            'cou.approver_id', user_ids,
            'cou.warehouse_id', warehouse_ids
        )
        start_date = '1990-01-01'
        end_date = '2100-01-01'

        if self.start_date:
            start_date = str(self.start_date)
        if self.end_date:
            end_date = str(self.end_date)
        self._cr.execute('delete from setu_inventory_count_report;')
        query = f"""
       select 
            count_line.product_id,
            cou.warehouse_id,
            count_line.location_id,
            cou.inventory_count_date,
            sum(coalesce(count_line.qty_in_stock,0))as theoretical_qty,
            sum(coalesce(count_line.counted_qty,0)) as counted_qty,
            abs(sum(coalesce(count_line.qty_in_stock,0)) - sum(coalesce(count_line.counted_qty,0))) as discrepancy_qty, 
            cou.approver_id as user_id,
            cou.id as count_id

        from setu_stock_inventory_count_line count_line
        inner join setu_stock_inventory_count cou on cou.id = count_line.inventory_count_id
        where cou.state in ('Inventory Adjusted','Approved')
        and count_line.is_discrepancy_found = 't'
        and cou.inventory_count_date::date >= '{str(start_date)}' and cou.inventory_count_date::date <= '{str(end_date)}'
        {where_query}
        group by
            count_line.product_id,
            cou.warehouse_id,
            count_line.location_id,
            cou.inventory_count_date,
            cou.approver_id,
            cou.id;
        """
        self._cr.execute(query)
        data_list = self._cr.dictfetchall()
        for data in data_list:
            self.create({
                'product_id': data['product_id'],
                'warehouse_id': data['warehouse_id'],
                'location_id': data['location_id'],
                'inventory_count_date': data['inventory_count_date'],
                'theoretical_qty': data['theoretical_qty'],
                'counted_qty': data['counted_qty'],
                'discrepancy_qty': data['discrepancy_qty'],
                'user_id': data['user_id'],
                'count_id': data['count_id']
            })
        action = self.sudo().env.ref('setu_inventory_count_management.setu_inventory_count_report_record_action').read()[0]
        return action
