from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        """
            Author: jatin.babariya@setconsulting
            Date: 24/03/25
            Task: Migration from V16 to V18.
            Purpose: When some fields of picking and cedis plan are match then create it's mail activity in current picking.
        """
        res = super(StockPicking, self)._action_done()
        for rec in self:
            if rec.picking_type_id.code:
                if rec.x_studio_sales_team:
                    plans = rec.track_warehouse_id.cedis_plan_ids.filtered(
                        lambda plan: plan.picking_type_id.id == rec.picking_type_id.id and
                                     plan.cliente_mostrador == rec.cliente_mostrador and
                                     plan.urgent_order == rec.urgent_order and
                                         plan.detener_factura == rec.x_studio_detener_factura)

                    team_plan = plans.filtered(
                        lambda plan: plan.sale_team_id.id == rec.x_studio_sales_team.id)
                    if len(team_plan) > 0:
                        self.create_cedis_plan_activity(team_plan, rec)
                    else:
                        team_plan_null = plans.filtered(lambda plan: plan.sale_team_id.id == False)
                        self.create_cedis_plan_activity(team_plan_null, rec)
                else:
                    plans = rec.track_warehouse_id.cedis_plan_ids.filtered(
                        lambda plan: plan.picking_type_id == rec.picking_type_id and
                                     plan.cliente_mostrador == rec.cliente_mostrador and
                                     plan.urgent_order == rec.urgent_order and
                                     plan.detener_factura == rec.x_studio_detener_factura and
                                     plan.sale_team_id.id == False)
                    self.create_cedis_plan_activity(plans, rec)
        return res

    def create_cedis_plan_activity(self, plans, rec):
        """
            Author: jatin.babariya@setconsulting
            Date: 24/03/25
            Task: Migration from V16 to V18.
            Purpose: To Create mail activity record.
        """
        for user_plan in plans:
            for user in user_plan.user_ids:
                activity = self.env['mail.activity'].create({
                    'activity_type_id': user_plan.activity_type_id.id,
                    'res_id': rec.id,
                    'res_model_id': rec.env.ref('stock.model_stock_picking').id,
                    'user_id': user.id,
                    'summary': user_plan.summary,
                    'note': user_plan.planning
                })
            activity.action_close_dialog()
