from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    oldest_stock_days = fields.Selection([('30_days', '30 Days'), ('60_days', '60 Days'), ('90_days', '90 Days'),
                                          ('120_days', '120 Days'), ('150_days', '150 Days'), ('180_days', '180 Days')],
                                         'Oldest Stock Count Days', default='30_days', help="From how many days you want to count Oldest Stock?")

