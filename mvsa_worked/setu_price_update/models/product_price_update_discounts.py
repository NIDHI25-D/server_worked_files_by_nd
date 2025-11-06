from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class ProductPriceUpdateDiscounts(models.Model):
    _name = 'product.price.update.discounts'
    _description = 'ProductPriceUpdateDiscounts'

    name = fields.Char(string="Discount")
    discount = fields.Integer("Discounts(%)", compute='_get_discount', store=True)

    @api.depends('name')
    def _get_discount(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used to check whether the record of Discount is_digit or not. If it's not digit it will raise an error
        """
        for rec in self:
            rec.discount = 0.0
            if rec.name.isdigit():
                rec.discount = int(rec.name)
            else:
                raise ValidationError(_("Please enter only digits"))

