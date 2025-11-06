from odoo.exceptions import ValidationError

from odoo import models, fields, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    oracle_upc = fields.Char('Oracle UPC')

    # def unlink(self):
    #     for record in self:
    #         if record.order_id.oracle_internal_id:
    #             msg = (_("You can not Delete this Order Line because line is attached with Oracle Order Line."))
    #             raise ValidationError(msg)
    #     return super(SaleOrderLine, self).unlink()
