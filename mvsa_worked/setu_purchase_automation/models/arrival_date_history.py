from odoo import models, fields, api


class ArrivalDateHistory(models.Model):
    _name = 'arrival.date.history'
    _order = 'id asc'
    _description = "Arrival Date History"

    update_date = fields.Date(string='Update Date')
    last_arrival_date = fields.Datetime(string='Last Arrival Date')
    change_reason_id = fields.Many2one('arrival.change.reason', string='Change Reason')
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Orders")