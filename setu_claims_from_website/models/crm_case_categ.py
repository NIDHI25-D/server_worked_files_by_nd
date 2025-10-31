from odoo import models, fields, api, _

class crm_case_categ(models.Model):
    """ Category of Case """
    _name = "crm.case.categ"
    _description = "Category of Case"

    @api.model
    def _find_object_id(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: This method is to set the object_id as claims/with respected modele in the moduel : crm.case.categ ie : categories
                    Finds id for case object
        """
        object_id = self.env.context.get('object_id', False)
        object_name = self.env.context.get('object_name', False)
        object_id = self.env['ir.model'].search(
            ['|', ('id', '=', object_id), ('model', '=', object_name)], limit=1)
        return object_id

    name = fields.Char('Name', required=True, translate=True)
    team_id = fields.Many2one('crm.team', 'Sales Team')
    object_id = fields.Many2one('ir.model', 'Object Name', default=_find_object_id)
    available_on_website = fields.Boolean(string="Available On Website", default=False)
