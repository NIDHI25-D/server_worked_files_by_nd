from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    date_custom_numbers = fields.Char(string="Date Custom Number")
    related_purchase_orders = fields.Many2many('purchase.order', compute='_compute_related_purchase_order', string="Related Purchase Orders", store=True)

    @api.depends('picking_ids')
    def _compute_related_purchase_order(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/03/25
            Task: Migration to v18 from v16
            Purpose: Show the picking related purchase order to landed costs.
        """
        for rec in self:
            if rec.picking_ids:
                rec.related_purchase_orders = [(6, 0, rec.picking_ids.mapped('purchase_id').ids)]
            else:
                rec.related_purchase_orders = False
        return True

    def button_validate(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/03/25
            Task: Migration to v18 from v16
            Purpose: raise validation if Customs number and which is not in draft or cancel and same picking are already not set in any others.
        """
        picking_id = self.search([('state', 'not in', ['draft', 'cancel'])]).mapped('picking_ids').filtered(
            lambda x: x.id in self.picking_ids.ids)
        if self.l10n_mx_edi_customs_number and picking_id:
            raise ValidationError(
                _("The custom number for picking (%s) is already created." % (', '.join(picking_id.mapped('name')))))
        return super(StockLandedCost, self).button_validate()
