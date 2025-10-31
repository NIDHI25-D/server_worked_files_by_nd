from odoo import models, fields, api


class SaleReport(models.Model):
    _inherit = 'sale.report'

    rutav = fields.Char(string='Ruta')
    zone_id = fields.Many2one('res.partner.zone', string="Zone")
    locality_id = fields.Many2one('l10n_mx_edi.res.locality', 'Delivery locality')
    delivery_partner_state_id = fields.Many2one('res.country.state', 'Delivery state')

    def _select_additional_fields(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: This method is to add fields in select query
        """
        res = super()._select_additional_fields()
        res['rutav'] = "partner.rutav"
        res['zone_id'] = "partner.zone_id"
        res['locality_id'] = "delivery_partner.l10n_mx_edi_locality_id"
        res['delivery_partner_state_id'] = "delivery_partner.state_id"
        return res 

    def _from_sale(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: This method is to add joins in from query
        """
        res = super()._from_sale()
        res += """ join res_partner delivery_partner ON (s.partner_shipping_id = delivery_partner.id) """
        return res

    def _group_by_sale(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
           Purpose: This method is to add fields in group_by query
        """
        res = super()._group_by_sale()
        res += """, partner.rutav, partner.zone_id, delivery_partner.l10n_mx_edi_locality_id , delivery_partner.state_id """
        return res
