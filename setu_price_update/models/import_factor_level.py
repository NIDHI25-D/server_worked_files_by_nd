from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ImportFactorLevel(models.Model):
    _name = 'import.factor.level'
    _description = 'import.factor.level'

    name = fields.Char(string="Import Factor Level")
    import_factor = fields.Float(store=True, compute='_get_import_factor')

    @api.depends('name')
    def _get_import_factor(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: In this method, it checks whether the factor level is_alpha or not. If it's not digit/float than it will raise error
        """
        for rec in self:
            rec.import_factor = 0.0
            if not rec.name.isalpha():
                rec.import_factor = float(rec.name)
            else:
                raise ValidationError(_("Please enter only digits"))
