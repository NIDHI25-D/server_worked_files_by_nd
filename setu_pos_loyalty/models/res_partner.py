from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty_points = fields.Float(string="Loyalty Points",
                                  help='The loyalty points the user won as part of a Loyalty Program.',
                                  compute="get_loyalty_points")

    def get_loyalty_points(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 13/05/2025
            Task: Migration from V16 to V18
            Purpose: This method used for search partner's loyalty card and update the points.
        """
        for rec in self:
            partner_lc_ids = self.env['loyalty.card'].sudo().search(
                [('partner_id', '=', rec.id), ('program_id.program_type', '=', 'loyalty'),('program_id.active','=',True)])
            if partner_lc_ids:
                rec.loyalty_points = sum(partner_lc_ids.mapped('points'))
            else:
                rec.loyalty_points = 0
