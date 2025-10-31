from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PriceLevelConfig(models.Model):
    _name = 'competition.level'
    _description = 'competition.level'
    # _rec_name = 'level'

    name = fields.Char(string="Level")
    level = fields.Integer(compute='_get_integer_level', store=True)
    price_base_ids = fields.One2many('price.bases', 'competition_level_id', string='Price Bases')
    final_profit_margin = fields.Float(string="Final Profit Margin")

    @api.depends('name')
    def _get_integer_level(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: In this method, it checks whether the competition level is digit or not. If it's not digit than it will raise error
        """
        _logger.debug("Compute _get_integer_level method start")
        for rec in self:
            rec.level = 0.0
            if rec.name.isdigit():
                rec.level = int(rec.name)
            else:
                raise ValidationError(_("Please enter only digits"))
        _logger.debug("Compute _get_integer_level method end")
