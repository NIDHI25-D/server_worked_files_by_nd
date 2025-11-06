from odoo import fields, models, _, api
from markupsafe import Markup


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def write(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: Used for see the history in message.
        """
        # Delete the product pricelist items
        old_value = self.env['product.pricelist'].browse(self.id)
        if vals.get('item_ids'):
            deleted_lst = []
            for item in vals.get('item_ids'):
                if item[0] == 2:
                    deleted_lst.append(item[1])
            deleted_value = self.env['product.pricelist.item'].browse(deleted_lst)
            lst_value = [(p.name, str(p.min_quantity), str(p.price), str(p.date_start), str(p.date_end)) for p in
                         deleted_value]
            deleted_msg = ""
            for order in lst_value:
                deleted_msg += _("%s ") % (' | '.join(order)) + "<br>"
    
            # Update the product pricelist items
            lst = []
            for item in vals.get('item_ids'):
                if item[0] == 1:
                    lst.append(item[1])
            previous_value = self.env['product.pricelist.item'].browse(lst)
            lst1 = [(p.name, str(p.min_quantity), str(p.price), str(p.date_start), str(p.date_end)) for p in previous_value]
            old_value_msg = ""
            for order in lst1:
                old_value_msg += _("%s ") % (' | '.join(order)) + "<br>"
            res = super(ProductPricelist, self).write(vals)
            latest_value = self.env['product.pricelist.item'].browse(lst)
            lst2 = [(p.name, str(p.min_quantity), str(p.price), str(p.date_start), str(p.date_end)) for p in latest_value]
            new_value_msg = ""
            for order in lst2:
                new_value_msg += _("%s ") % (' | '.join(order)) + "<br>"
    
            if lst and deleted_lst:
                self.message_post(body=Markup(_(
                    f"Old Value:- <br>{old_value_msg} <br> New Value:- <br>{new_value_msg} <br> Deleted Value:- <br>{deleted_msg}")))
            elif deleted_lst and not lst:
                self.message_post(body=Markup(_(f"Deleted Value:- <br>{deleted_msg}")))
            elif lst and not deleted_lst:
                self.message_post(body=Markup(_(f"Old Value:- <br>{old_value_msg} <br> New Value:- <br>{new_value_msg}")))
            return res
        else:
            return super(ProductPricelist, self).write(vals)

