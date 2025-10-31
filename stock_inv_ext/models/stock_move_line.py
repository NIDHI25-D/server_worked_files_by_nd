from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, readonly=True)
    responsible_person = fields.Many2one('hr.employee', string="Responsible",
                                         compute='_compute_responsible_person',
                                         inverse='_inverse_responsible_person_set')

    def _compute_responsible_person(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: set the Responsible of the move line as per the transfer.
        """
        for rec in self:
            rec.responsible_person = rec.picking_id.responsible_person.id

    def _inverse_responsible_person_set(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: same inverse set transfer's Responsible from line's Responsible.
        """
        for rec in self:
            rec.picking_id.responsible_person = rec.responsible_person.id


    def _get_aggregated_product_quantities(self, **kwargs):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: This method is inherited to get location_id(FROM) in aggregate_line of delivery slip report
        """
        res = super(StockMoveLine, self)._get_aggregated_product_quantities()
        for move_line in self:
            if move_line.move_id.picking_type_id.code == 'internal' and move_line.move_id.group_id.sale_id:
                location = self.browse(move_line.location_id).id
                product = move_line.browse(move_line.product_id).id
                for data in res.values():
                    if data.get('product') == self.browse(product).id:
                        data.update({'location_id': location})
        return res
