from odoo import models, fields, api, _
from ast import literal_eval
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round
import logging

_logger = logging.getLogger("price_level_config")

class PriceLevelConfig(models.Model):
    _name = 'price.level.config'
    _description = 'price.level.config'
    _inherit = ['mail.thread']

    def unlink(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used to delete the records which in state --> Draft
        """
        if any(self.filtered(lambda plc: plc.state not in ('draft'))):
            raise UserError(_('You cannot delete a record which is not draft'))
        return super(PriceLevelConfig, self).unlink()

    def _get_default_range1(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: To get range1 field value from config parameter.
                     :return:
        """
        return int(self.env['ir.config_parameter'].sudo().get_param('setu_price_update.range1')) or 0

    def _get_default_range2(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: To get range2 field value from config parameter.
                     :return:
        """
        return int(self.env['ir.config_parameter'].sudo().get_param('setu_price_update.range2')) or 0

    def _get_default_import_factor(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: To get import_factor field value from config parameter.
                     :return:
        """
        return float(self.env['ir.config_parameter'].sudo().get_param('setu_price_update.import_factor')) or 0.0

    def _get_default_level(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: To get level field value from config parameter.
                     :return:
        """
        return int(self.env['ir.config_parameter'].sudo().get_param('setu_price_update.level')) or False

    def _get_default_responsible(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: To get level field value from config parameter.
                     :return:
        """

        return int(self.env['ir.config_parameter'].sudo().get_param('setu_price_update.responsible_id')) or False

    def _get_default_exchange_rate(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: To get exchange_rate field value from config parameter.
                     :return:
        """
        return float(self.env['ir.config_parameter'].sudo().get_param('setu_price_update.exchange_rate')) or 0.0

    def _get_default_discounts(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: To get discount_ids field value from config parameter.
                     :return:
        """
        return literal_eval(self.env['ir.config_parameter'].sudo().get_param('setu_price_update.discount_ids')) or []

    name = fields.Char(string="Name", readonly=True, required=True, copy=False, default='New')
    level_id = fields.Many2one('competition.level', string="Level", default=_get_default_level)
    first_range = fields.Integer(string='Range 1', default=_get_default_range1)
    second_range = fields.Integer(string='Range 2', default=_get_default_range2)
    level_range = fields.Float(string='Level Range', compute="_compute_level_range")
    exchange_rate = fields.Float(string='Exchange Rate', default=_get_default_exchange_rate)
    discount = fields.Float(string="Discount")
    import_factor = fields.Float(string="Import Factor", default=_get_default_import_factor)
    level_ids = fields.One2many('price.level', 'config_id', string="Levels")
    product_level_ids = fields.One2many('product.price.level', 'config_id', string="Product Levels")
    responsible_person_id = fields.Many2one('res.users', string="Responsible", default=_get_default_responsible)
    base_exchange_rate = fields.Float("Base exchange rate")
    discount_ids = fields.Many2many('product.price.update.discounts', 'plc_discount_rel', 'plc_id', 'disc_id',
                                    string="Discounts", default=_get_default_discounts, ondelete="restrict")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('original', 'Changed To Original')
    ], string='Status', readonly=True, default='draft')
    include_negative_increments = fields.Boolean(string="Include Negative Increments")

    @api.onchange('level_id')
    def check_products_of_levels(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used to check the levels and it will raise the error when the product level is set and then the level_id is changed.
        """
        price_level_with_less_level = self.product_level_ids.product_id.filtered(lambda p:p.product_tmpl_id.competition_level_id.level > self.level_id.level)
        if price_level_with_less_level:
            raise UserError(_("You can't change the level because there is some product level having less competition level then you have selected"))

    def _compute_level_range(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used to calculate the level_range which is further used in _compute_level_Percentage to calculate the Level Percentage
        """
        _logger.debug("Compute _compute_level_range method start")
        for res in self:
            res.level_range = 0
            # formula = (R1 - R2) / L
            if res.level_id.level > 0:
                res.level_range = (abs(res.first_range - res.second_range)) / res.level_id.level
        _logger.debug("Compute _compute_level_range method end")

    def action_set_levels(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is called for Generate levels smart button.This button will create a range from 0 to
                     the given number of level. It will create the price level upto the range. It will also assign
                      level percentage and complement
        """
        self.level_ids.unlink()
        for res in range(self.level_id.level):
            price_level = self.env['price.level'].sudo().create({
                'name': res + 1,
                'config_id': self.id
            })
            price_level._compute_level_Percentage()
            price_level._compute_level_complement()

    def update_price(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used to update the price and stage to the second approval. It will raise error if update price is less than current price
        """
        if self.product_level_ids:
            existing_records = self.search([])
            present_in_previous_record = existing_records.filtered(lambda o: o.state == 'validate1').product_level_ids.filtered(lambda pl: pl.product_id.id in self.product_level_ids.product_id.ids)
            if present_in_previous_record:
                pro = present_in_previous_record.product_id.mapped('name')
                raise UserError(_(f"{pro} Products are already in second approval stage"))
            to_approve = True
            display_msg = """ Price is not updated because the new price of following products is less then the actual price """""",
                                                               <br/>
                                                           """
            if not self.include_negative_increments:
                for line in self.product_level_ids.filtered(lambda pl: pl.marvel_price < pl.Price):
                    # if not line.marvel_price >= line.Price:
                    to_approve = False
                    display_msg += """ - """
                    display_msg += f"""[{line.product_id.default_code}] {line.product_id.name}"""
                    display_msg += """ <br/> """
                    _logger.info(_(f"The price  is not updated because the new price of product '{line.product_id.name}' is less then the actual price "))
            else:
                if self.product_level_ids.filtered(lambda p: p.marvel_price >= p.Price):
                    msg = "The price of some product may be less then the actual price because this record allowed the negative increments"
                    self.message_post(body=msg)
            if to_approve:
                self.message_post(body=_(f"The state has changed from {self.state}  to Second Approval"))
                self.state = 'validate1'
            else:
                self.state = 'draft'
                self.message_post(body=display_msg)

    def update_price_in_odoo(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used to set the updated marvel_price of price.level.config to the product's list_price
        """
        display_msg = f""" The price has been updated by {self.env.user.name}"""""",<br/>"""
        for line in self.product_level_ids:
            line.previous_Price = line.product_id.lst_price
            line.product_id.lst_price = line.marvel_price
            display_msg += """ - """
            display_msg += f""" [{line.product_id.default_code}] {line.product_id.name}   {line.previous_Price} ==> {line.marvel_price}"""
            display_msg += """ <br/> """
            _logger.info(_(f"The price of product '{line.product_id.name}' is changed form '{line.previous_Price}' to '{line.marvel_price}'"))
        self.state = 'validate'
        self.message_post(body=display_msg)

    def change_price_to_previous(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used update the price to the original price as well as update the state to ORIGINAL and message in chatter
        """
        display_msg = f""" The price has been changed to previous price by {self.env.user.name} """""", <br/>"""
        for line in self.product_level_ids:
            pre_price = line.product_id.lst_price
            line.product_id.lst_price = line.previous_Price
            display_msg += """ - """
            display_msg += f""" [{line.product_id.default_code}] {line.product_id.name}   {pre_price} ==> {line.product_id.lst_price}"""
            display_msg += """ <br/> """
            _logger.info(_(f"The price of product '{line.product_id.name}' is changed form '{pre_price}' to '{line.product_id.lst_price}'"))
        self.state = 'original'
        self.message_post(body=display_msg)

    @api.model_create_multi
    def create(self, values):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used create the Price level config and set the name as per the sequence
        """
        for val in values:
            seq = self.env['ir.sequence'].next_by_code('price.config') or 'New'
            val['name'] = seq
        return super(PriceLevelConfig, self.sudo()).create(values)

    def calculate_marvel_price(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is called for "Calculate new price" smart button. In this method it will calculate "NEW PRICE" i.e. marvel_price with calculation of exchange_rate,import_factor,price_complement
        """
        for level in self.product_level_ids:
            price_disc = 0
            if level.cost_price:
                for disc in level.config_id.discount_ids:
                    if not price_disc:
                        price_disc = ((((level.cost_price * level.config_id.exchange_rate) * level.config_id.import_factor) / level.config_id.level_ids.filtered(
                            lambda l: int(l.name) == level.product_id.competition_level_id.level).price_complement) / (
                                              1 - (disc.discount / 100))) if level.config_id.level_ids.filtered(
                            lambda l: int(l.name) == level.product_id.competition_level_id.level) else 0
                    else:
                        price_disc = price_disc / (1 - (disc.discount / 100))
                level.marvel_price = float_round(float_round(price_disc, 2), 1)
            else:
                level.marvel_price = level.Price
