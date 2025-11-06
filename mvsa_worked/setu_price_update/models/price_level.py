from odoo import models, fields, api, _

class price_level(models.Model):
    _name = 'price.level'
    _description = 'Price level based on level configuration'

    name = fields.Char(string="Levels")
    level_Percentage = fields.Float(string='Level Percentage', compute='_compute_level_Percentage')
    price_complement = fields.Float(string='Level Complement', compute='_compute_level_complement')
    config_id = fields.Many2one("price.level.config", "Related Configuration")

    def _compute_level_Percentage(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used to calculate the level percentage present in tab levels
        """
        for res in self:
            res.level_Percentage = 0
            try:
                # formula = R1 + ((lr) * (l-1))
                res.level_Percentage = res.config_id.first_range + (
                        res.config_id.level_range * (int(res.name) - 1))
            except ValueError:
                res.level_Percentage = 0

    def _compute_level_complement(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used to calculate the price_complement present in tab levels
        """
        for res in self:
            res.price_complement = 0
            try:
                # formula = 1 - (pe  / 100)
                res.price_complement = 1 - (res.level_Percentage / 100)
            except ValueError:
                res.price_complement = 0
