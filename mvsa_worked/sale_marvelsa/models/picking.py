# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_studio_sales_team = fields.Many2one(related='sale_id.team_id', string='Sales Team', store=True)
    coupon_point_ids = fields.One2many(related='sale_id.coupon_point_ids')
    from_location_id = fields.Many2one(related='move_line_ids.location_id', string='From')
    to_location_id = fields.Many2one(related='move_line_ids.location_dest_id', string='To')
