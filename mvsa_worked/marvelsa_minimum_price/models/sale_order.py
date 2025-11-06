from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def check_min_price(self, order=None):
        """
              Author: jay.garach@setuconsulting.com
              Date:  10/12/24
              Task: Migration from V16 to V18
              Purpose: This method will match the currency with the company currency,it will prepare the list of the products
                    whose price mentioned in sale order will be less than the minimum price.To solve the issue of error
                    change the price in particular category of the product
                    Return : List of the products
        """
        company = self.env.user.company_id
        diff_currency = False
        lst = []
        if order:
            if order.pricelist_id:
                if order.pricelist_id.currency_id != company.currency_id:
                    diff_currency = True

            for order_line_id in order.order_line:
                if order_line_id.is_reward_line:
                    continue
                price_unit = order_line_id.price_unit
                product_original_price = price_unit - ((price_unit * order_line_id.discount)/100)
                if diff_currency:
                    price_unit = order.pricelist_id.currency_id._convert(price_unit, company.currency_id, company,
                                                                         order.date_order or fields.Date.today())
                else:
                    price_unit = product_original_price
                if order_line_id.product_id and (price_unit < order_line_id.product_id.minimum_price) and order_line_id.product_id.type != 'service':
                    lst.append(order_line_id.product_id.display_name)
        else:
            for order in self:
                if order.pricelist_id:
                    if order.pricelist_id.currency_id != company.currency_id:
                        diff_currency = True

                for line in order.order_line:
                    # line.is_reward_line is needed for free product on promotions program
                    if line.is_reward_line:  #no reward_line so commented
                        continue
                    price_unit = line.price_unit
                    product_original_price = price_unit - ((price_unit * line.discount)/100)
                    if diff_currency:
                        price_unit = order.pricelist_id.currency_id._convert(price_unit, company.currency_id, company,
                                                                             order.date_order)
                    else:
                        price_unit = product_original_price
                    if line.product_id and (price_unit < line.product_id.minimum_price) and line.product_id.type != 'service':
                        lst.append(line.product_id.display_name)
        return lst

    @api.model_create_multi
    def create(self, vals_list):
        """
            Author: jay.garach@setuconsulting.com
            Date:  10/12/24
            Task: Migration from V16 to V18
            Purpose: While creation of sale. Order, it will check the minimum price of the product as per the product category
                    and will generate the error if its lower
        """
        res = super(SaleOrder, self).create(vals_list)
        for vals in vals_list:
            if 'order_line' in vals.keys():
                config = self.env['ir.config_parameter'].sudo().get_param('marvelsa_minimum_price.enable_minimum_price')
                if config:
                    lst = res.check_min_price()
                    main_lst = [i for i in lst]
                    if main_lst:
                        main = '\n'.join(map(str, main_lst))
                        raise UserError(
                            _(f"Price is lower than the minimum product price !\nPlease recheck \n{main}\nor\nApply the discount according to minimum price"))
        return res

    def write(self, vals):
        """
            Author: jay.garach@setuconsulting.com
            Date: 10/12/24
            Task: Migration from V16 to V18
            Purpose: While updating/write/confirms of sale. Order, it will check the minimum price of the product as per the product category
                    and will generate the error if its lower
        """
        res = super(SaleOrder, self).write(vals)
        if 'order_line' in vals.keys():
            config = self.env['ir.config_parameter'].sudo().get_param('marvelsa_minimum_price.enable_minimum_price')
            if config:
                lst = self.check_min_price()
                main_lst = [i for i in lst]
                if main_lst:
                    main = '\n'.join(map(str, main_lst))
                    raise UserError(
                        _(f"Price is lower than the minimum product price !\nPlease recheck \n{main}\nor\nApply the discount according to minimum price"))
        if vals.get('state'):
            if vals.get('state') == 'cancel':
                return res
        return res

