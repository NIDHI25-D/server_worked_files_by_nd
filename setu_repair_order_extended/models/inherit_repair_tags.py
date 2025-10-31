from odoo import fields, models, api


class RepairTags(models.Model):
    _inherit = 'repair.tags'

    template_note = fields.Html(string='Add template note')