# -*- coding: utf-8 -*-
from odoo import fields, models


class SetuInvUserStatesReport(models.TransientModel):
    _name = 'setu.inventory.user.states.report'
    _inherit = 'setu.inventory.reporting.template'
    _description = 'Inventory User Statistics Report'

    sessions = fields.Integer(string="Total Sessions")

    discrepancy_ratio = fields.Float(string="Discrepancy")
    user_mistake_ratio = fields.Float(string="Calculation Mistake")

    def generate_report(self):
        self._cr.execute('delete from setu_inventory_user_states_report;')
        query = """
        with mix_data as(
            select
                unnest(users) as user_id,
                --discrepancy,
                user_mistake,
                product_id,
                session_id
            from
                (select 
                    --bool_or(is_discrepancy_found)as discrepancy,
                    bool_or(user_calculation_mistake)as user_mistake,
                    product_id,
                    session_id,
                    users 
                from 
                    (select 
                        sl.id as line_id,
                        ses.id as session_id,
                        sl.product_id,
                        array_agg(rel.res_users_id) as users,
                        --sl.is_discrepancy_found,
                        sl.user_calculation_mistake
                    from 
                        setu_inventory_count_session_line sl
                        inner join setu_inventory_count_session ses on ses.id = sl.session_id and ses.state = 'Done'
                        inner join res_users_setu_inventory_count_session_rel rel on ses.id = setu_inventory_count_session_id
                        group by sl.id,ses.id,sl.product_id
                        order by sl.product_id
                    )session_lines
                group by 
                    product_id,
                    session_id,
                    users)data
        )
        select 
            user_id,
            --(select count(md2.*) from mix_data md2 where md2.user_id = md.user_id and md2.discrepancy = true)::float*100/
            --(select count(*) from mix_data where user_id = md.user_id)::float as discrepancy_ratio,
            (select count(md2.*) from mix_data md2 where md2.user_id = md.user_id and md2.user_mistake = true)::float*100/
            (select count(*) from mix_data where user_id = md.user_id)::float as user_mistake_ratio,
            count(distinct session_id) as sessions
        from 
            mix_data md
        group by 
            user_id;
        """
        self._cr.execute(query)
        data_list = self._cr.dictfetchall()
        for data in data_list:
            self.create({'user_id': data['user_id'],
                         'user_mistake_ratio': round(data['user_mistake_ratio'], 2),
                         'sessions': data['sessions']})

        action = self.sudo().env.ref('setu_inventory_count_management.setu_inventory_user_states_report_action').read()[
            0]
        return action
