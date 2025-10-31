from odoo import api, fields, models, _
import random
from odoo.osv import expression
import ast
from collections import defaultdict
from odoo.fields import Command


def _generate_random_reward_code():
    return str(random.getrandbits(32))


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_reward_values_discount(self, reward, coupon, **kwargs):
        """
        Author: jay.garach@setuconsulting.com
        Date: 16/12/23
        Task: Migration from V16 to V18
        Purpose: to archive the task requirement to create the e-wallet lines as discount lines
        means assigning the e-wallet points as per line with the different types of tax.
        as per sale order lines the remaining amount and tax will assign the amount of the points to that line.
        return the dict of e-wallet line to be create.
        """
        if reward.program_id.program_type == 'ewallet':
            discountable = 0
            discountable_per_tax = defaultdict(int)
            reward_applies_on = reward.discount_applicability
            sequence = max(self.order_line.filtered(lambda x: not x.is_reward_line).mapped('sequence'), default=10) + 1
            if reward_applies_on == 'order':
                discountable, discountable_per_tax = self._discountable_order(reward)
            max_discount = reward.currency_id._convert(reward.discount_max_amount, self.currency_id, self.company_id,
                                                       fields.Date.today(), False) or float('inf')
            # discount should never surpass the order's current total amount
            max_discount = min(self.amount_total, max_discount)
            if reward.discount_mode == 'per_point':
                points = self._get_real_points_for_coupon(coupon)
                if not reward.program_id.is_payment_program:
                    # Rewards cannot be partially offered to customers
                    points = points // reward.required_points * reward.required_points
                max_discount = min(max_discount,
                                   reward.currency_id._convert(reward.discount * points,
                                                               self.currency_id, self.company_id, fields.Date.today(),
                                                               False))
            reward_code = _generate_random_reward_code()
            reward_dict = {}
            for tax, price in discountable_per_tax.items():
                if not price:
                    continue
                total_price_unit = ((price * max_discount) / discountable)
                price_unit = total_price_unit
                mapped_taxes = self.fiscal_position_id.map_tax(tax)
                tax_amount_total = 0
                for tax_id in mapped_taxes:
                    if tax_id.children_tax_ids:
                        for children_tax_id in tax_id.children_tax_ids:
                            if (not children_tax_id.price_include or children_tax_id.include_base_amount):
                                tax_amount_total += children_tax_id.amount
                        continue
                    if (not tax_id.price_include or tax_id.include_base_amount):
                        tax_amount_total += tax_id.amount
                price_unit = ((price_unit * 100) / (100 + tax_amount_total))
                if (taxes_ids := [tax for tax in mapped_taxes if tax.include_base_amount]
                                 or [child_tax for child_tax in mapped_taxes.children_tax_ids if
                                     child_tax.include_base_amount]):
                    total_void_amount = 0
                    for taxes_id in taxes_ids:
                        if taxes_id.price_include:
                            total_void_amount += taxes_id.amount
                        else:
                            continue
                    price_unit = ((price_unit * (1.0 + total_void_amount / 100.0)))
                if reward.discount_mode == 'per_point' and not reward.clear_wallet:
                    # Calculate the actual point cost if the cost is per point
                    converted_discount = self.currency_id._convert(total_price_unit,
                                                                   reward.currency_id, self.company_id,
                                                                   fields.Date.today(), False)
                    total_price_unit = converted_discount / reward.discount
                tax_desc = _(
                    ' - On product with the following taxes: %(taxes)s',
                    taxes=", ".join(mapped_taxes.mapped('name')),
                )
                reward_dict[tax] = {
                    'name': _(
                        'Ewallet: %(desc)s%(tax_str)s',
                        desc=reward.description,
                        tax_str=tax_desc,
                    ),
                    'product_id': reward.discount_line_product_id.id,
                    'price_unit': -min(price_unit, discountable),
                    'product_uom_qty': 1.0,
                    'product_uom': reward.discount_line_product_id.uom_id.id,
                    'reward_id': reward.id,
                    'coupon_id': coupon.id,
                    'points_cost': total_price_unit,
                    'reward_identifier_code': reward_code,
                    'sequence': sequence,
                    'tax_id': [Command.clear()] + [Command.link(tax.id) for tax in mapped_taxes]
                }
            return list(reward_dict.values())
        else:
            return super(SaleOrder, self)._get_reward_values_discount(reward, coupon, **kwargs)

    def _discountable_order(self, reward):
        """
        Author: jay.garach@setuconsulting.com
        Date: 16/12/23
        Task: Migration from V16 to V18
        Purpose: we are retrieving the data of the remaining amount of sale orders per line it will
        consider the included amount after compiled by the tax. the included amount is not considering
        the discount so we have to manually remove the amount of discount from that line to get the
        total amount that is remaining.

        Returns the discountable:- The total amount that remaining in sale order (amount)
        discountable_per_tax :- it will give the line wise data (dict)
        {'tax_id': amount}
        tax_id :- having the id or ids as per line of product configration
        amount :- the remaing amount line
        """
        if reward.program_id.program_type == 'ewallet':
            self.ensure_one()
            if reward.discount_applicability == 'order':
                discountable_per_tax = defaultdict(int)
                lines = self.order_line if reward.program_id.is_payment_program else (
                        self.order_line - self._get_no_effect_on_threshold_lines())
                total_tax_ids_count = 0
                for line in lines:
                    # Ignore lines from this reward
                    if not line.product_uom_qty or not line.price_unit or line.reward_id.program_id.program_type == 'ewallet':
                        continue
                    tax_data = line.tax_id.compute_all(
                        line.price_unit,
                        quantity=line.product_uom_qty,
                        product=line.product_id,
                        partner=line.order_partner_id,
                    )
                    if line.discount:
                        total_included = tax_data.get('total_included')
                        tax_data['total_included'] = total_included - (total_included * (line.discount / 100))
                    total_tax_ids_count += tax_data.get('total_included')
                    discountable_per_tax[line.tax_id] += tax_data.get('total_included')
                discountable = total_tax_ids_count
                return discountable, discountable_per_tax
        else:
            return super(SaleOrder, self)._discountable_order(reward)

    def _program_check_compute_points(self, programs):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/12/23
            Task: Migration from V16 to V18
            Purpose: get sale order.
        """
        res = super(SaleOrder, self)._program_check_compute_points(programs)
        programs._get_valid_sale_order(self)
        return res

    def _get_claimable_rewards(self, forced_coupons=None):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/12/23
            Task: Migration from V16 to V18
            Purpose: check whether the current sale order are same as domain then apply reward else not.
        """
        result = super(SaleOrder, self)._get_claimable_rewards()
        rule_sale = dict()
        all_coupons = forced_coupons or (
                self.coupon_point_ids.coupon_id | self.order_line.coupon_id | self.applied_coupon_ids)
        global_discount_reward = self._get_applied_global_discount()
        for rule in all_coupons.program_id.rule_ids:
            domain = []
            if rule.sale_domain and rule.sale_domain != '[]':
                domain = expression.AND([domain, ast.literal_eval(rule.sale_domain)])
            if domain:
                rule_sale[rule] = self.filtered_domain(domain)
            else:
                rule_sale[rule] = self

            if not rule_sale[rule]:
                for reward in rule.program_id.reward_ids:
                    if not reward.is_global_discount and global_discount_reward and global_discount_reward.discount >= reward.discount:
                        remove_reward_by_applying_domain = [key for key, value in result.items() if value == reward]
                        for key in remove_reward_by_applying_domain:
                            del result[key]

                remove_reward_by_applying_domain = [key for key, value in result.items() if
                                                    value == rule.program_id.reward_ids]
                for key in remove_reward_by_applying_domain:
                    del result[key]

        return result
