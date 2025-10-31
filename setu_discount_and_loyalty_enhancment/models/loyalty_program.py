from odoo import _, api, fields, models


class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    need_to_exclude_from_automatic_sign = fields.Boolean(string="Need To Exclude From Automatic Sign")

    def _program_type_default_values(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/12/23
            Task: Migration from V16 to V18
            Purpose: Made a changes for save a first rule at first attempt
        """
        res = super()._program_type_default_values()
        res['promotion']['rule_ids'] = [(6, 0, [])]
        return res

    def _get_valid_sale_order(self, sales):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/12/23
            Task: Migration from V16 to V18
            Purpose: filtered sale order domain if getting.
        """
        rule_sale = dict()
        for rule in self.rule_ids:
            domain = rule._get_valid_sale_domain()
            if domain:
                rule_sale[rule] = sales.filtered_domain(domain)
            else:
                rule_sale[rule] = sales
        return rule_sale
