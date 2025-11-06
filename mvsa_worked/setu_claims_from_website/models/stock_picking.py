# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    claim_id = fields.Many2one('crm.claim', string="Claim")

    @api.onchange('claim_id', 'date_order_received', 'shipping_carrier_id', 'x_studio_fecha_de_envio',
                  'x_studio_fecha_de_entrega')
    def _onchange_claim_state(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: setting the sage into claims upon automation on dates.
        """
        claim_en_envio_stage_id = self.env['crm.claim.stage'].search([('sequence', '=', 4)])
        claim_en_transito_stage_id = self.env['crm.claim.stage'].search([('sequence', '=', 5)])
        claim_entregado_stage_id = self.env['crm.claim.stage'].search([('sequence', '=', 6)])
        if self.claim_id and self.date_order_received and self.claim_id.stage_id.sequence < claim_en_envio_stage_id.sequence:
            self.claim_id.stage_id = claim_en_envio_stage_id.id

        if self.claim_id and self.shipping_carrier_id and self.x_studio_fecha_de_envio and self.claim_id.stage_id.sequence < claim_en_transito_stage_id.sequence:
            self.claim_id.stage_id = claim_en_transito_stage_id.id

        if self.claim_id and self.x_studio_fecha_de_entrega and self.claim_id.stage_id.sequence < claim_entregado_stage_id.sequence:
            self.claim_id.stage_id = claim_entregado_stage_id.id

    def _action_done(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: setting claim stage which have a sequence is 3.
        """
        res = super(StockPicking, self)._action_done()
        for picking in self:
            claim_en_surtido_stage_id = self.env['crm.claim.stage'].search([('sequence', '=', 3)])
            if picking.claim_id and picking.claim_id.stage_id.sequence < claim_en_surtido_stage_id.sequence:
                picking.claim_id.stage_id = claim_en_surtido_stage_id.id
        return res
