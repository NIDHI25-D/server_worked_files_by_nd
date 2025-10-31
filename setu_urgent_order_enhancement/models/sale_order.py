from odoo import fields, models, api
from ast import literal_eval


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_urgent_order = fields.Boolean(string="Urgent Order")

    @api.model_create_multi
    def create(self, vals):
        """
            Author: jay.garach@setuconsulting.com
            Date: 10/01/25
            Task: Migration from V16 to V18
            Purpose: if sale order's customer or selected sales team store in the
                     system parameter (Which are set from the settings-> sales -> Urgent Orders),
                     then is_urgent_order field set to True automatically.
        """

        record = super(SaleOrder, self).create(vals)
        for res in record:
            enable_platforms_urgent_order = literal_eval(self.env['ir.config_parameter'].sudo().get_param(
                'setu_urgent_order_enhancement.urgent_orders_sales_team_ids') or '[]')
            if res.partner_id.is_urgent_order or res.team_id.id in enable_platforms_urgent_order:
                res.is_urgent_order = True
        return record

    @api.onchange('partner_id', 'team_id')
    def onchange_method(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 10/01/25
            Task: Migration from V16 to V18
            Purpose: After creating the sale order if a partner or sales team was changed,
                 then is_urgent_order fields set automatically according to the setting.
        """
        enable_platforms_urgent_order = literal_eval(self.env['ir.config_parameter'].sudo().get_param(
            'setu_urgent_order_enhancement.urgent_orders_sales_team_ids') or '[]')
        if self.partner_id.is_urgent_order or self.team_id.id in enable_platforms_urgent_order:
            self.is_urgent_order = True
        else:
            self.is_urgent_order = False

    def write(self, vals):
        """
            Author: jay.garach@setuconsulting.com
            Date: 10/01/25
            Task: Migration from V16 to V18
            Purpose: if sale order's customer or selected sales team store in the
                     system parameter (Which are set from the settings-> sales -> Urgent Orders),
                     then is_urgent_order field set to True automatically.
        """
        if vals.get('partner_id') or vals.get('team_id'):
            partner_id = vals.get('partner_id') or self.partner_id.id
            team_id = vals.get('team_id') or self.team_id.id
            partner = False
            if partner_id:
                partner = self.env['res.partner'].browse(partner_id)
            enable_platforms_urgent_order = literal_eval(self.env['ir.config_parameter'].sudo().get_param(
                'setu_urgent_order_enhancement.urgent_orders_sales_team_ids') or '[]')
            if partner.is_urgent_order or team_id in enable_platforms_urgent_order:
                vals.update({'is_urgent_order': True})
            else:
                vals.update({'is_urgent_order': False})
        return super(SaleOrder, self).write(vals)
