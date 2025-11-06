# -*- coding: utf-8 -*-
from odoo import models


class ProductPriceList(models.Model):
    _inherit = "product.pricelist"

    def get_product_price_from_pricelist(self, product_id, partner_id=False):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will get product price
        :param product_id:
        :param partner_id:
        :return: product price
        """
        product_price = self._get_product_price(product_id, 1.0, partner=partner_id,
                                                uom_id=partner_id and partner_id.uom_id.id)
        return product_price

    def set_product_price_from_pricelist(self, product_id, price, min_qty=1):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use for set product price in price-list item
        :param product_id:
        :param price:
        :param min_qty:
        :return: pricelist item recordset
        """
        product_pricelist_item_obj = self.env['product.pricelist.item']
        product_pricelist_item_id = product_pricelist_item_obj.search(
            [('pricelist_id', '=', self.id), ('product_id', '=', product_id and product_id.id),
             ('min_quantity', '=', min_qty)])
        if product_pricelist_item_id:
            product_pricelist_item_id.write({'fixed_price': float(price)})
        else:
            vals = {'pricelist_id': self.id,
                    'product_tmpl_id': product_id.product_tmpl_id and product_id.product_tmpl_id.id,
                    'applied_on': '0_product_variant', 'product_id': product_id and product_id.id,
                    'min_quantity': min_qty, 'fixed_price': price}
            new_record = product_pricelist_item_obj.new(vals)
            new_record._onchange_product_id()
            new_vals = product_pricelist_item_obj._convert_to_write(
                {name: new_record[name] for name in new_record._cache})
            product_pricelist_item_id = product_pricelist_item_obj.create(new_vals)
        return product_pricelist_item_id
