from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def write(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: In this method, crm stage is modified to
                        shipped stage if all the x_studio_fecha_de_envio dates of stock.picking are true  and
                        won stage if all the x_studio_fecha_de_entrega of stock.picking are true
        """
        res = super(StockPicking, self).write(vals)
        if self.sale_id.opportunity_id and 'x_studio_fecha_de_envio' in vals.keys():
            if not (False in self.filtered(lambda p: p.state != 'cancel' and p.picking_type_id.code == 'outgoing').mapped('x_studio_fecha_de_envio')):
                shipped_stage_id = self.env.ref('setu_crm_automation.shipped_stage').id
                self.sale_id.opportunity_id.with_context(is_from_sale_order=True).stage_id = shipped_stage_id
        if self.sale_id.opportunity_id and 'x_studio_fecha_de_entrega' in vals.keys():
            if not (False in self.sale_id.opportunity_id.order_ids.filtered(lambda o: o.state != 'cancel').picking_ids.filtered(lambda p: p.state != 'cancel' and p.picking_type_id.code == 'outgoing').mapped('x_studio_fecha_de_entrega')):
                won_id = self.env.ref('crm.stage_lead4')
                won_stage_id = self.env['crm.stage'].browse(won_id).id
                self.sale_id.opportunity_id.with_context(is_from_sale_order=True).stage_id = won_stage_id
        return res
    
