from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def check_minimum_price(self):
        """
            Author: jay.garach@setuconsulting.com
            Date:  10/12/24
            Task: Migration from V16 to V18
            Purpose: This method will check the minimum price --Price of the account.move
        """
        company = self.env.user.company_id
        diff_currency = False

        for rec in self:
            if rec.currency_id != company.currency_id:
                diff_currency = True

            for line in rec.invoice_line_ids:
                price_unit = line.price_unit
                if diff_currency:
                    price_unit = rec.currency_id._convert(
                        price_unit, company.currency_id, company, rec.invoice_date or fields.Date.today())
                    # line.is_reward_line is needed for free product on promotions program
                    # if not line.is_reward_line and...is removed as the field is_reward_line is not there--4/5/2023
                    if line.product_id and line.product_id.type != 'service' and (
                            price_unit < line.product_id.minimum_price) and not line.is_reward_line:
                        raise UserError(_("Price is lower than the minimum product price! \n Please recheck %s") % (
                            line.product_id.name))
        return True

    def action_post(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 10/12/24
            Task: Migration from V16 to V18
            Purpose: This method is called when invoice will be created.Here it will also check the minimum price
        """
        for account_rec in self:
            if account_rec.move_type == 'out_invoice':
                config = self.env['ir.config_parameter'].sudo().get_param('marvelsa_minimum_price.enable_minimum_price')
                if config:
                    account_rec.check_minimum_price()
        return super(AccountMove, self).action_post()

    def delete_invoice_lines(self):
        """
            Author: jay.garach@setuconsulting.com
            Date:  10/12/24
            Task: Migration from V16 to V18
            Purpose: This method will delete all the invoice lines of credit note. Procedure : Sale_order->invoice->Add to credit note
        """
        self.ensure_one()
        self.invoice_line_ids = [(5,)]
