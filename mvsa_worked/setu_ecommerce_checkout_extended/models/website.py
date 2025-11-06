from odoo import api, fields, models

class website(models.Model):

    _inherit = 'website'

    hcategory_id = fields.Many2one(
        comodel_name='res.partner.hcategory',
        string='Category',
    )