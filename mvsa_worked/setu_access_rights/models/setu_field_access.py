from odoo import fields, models, api

class SetuFieldAccess(models.Model):
    _name = "setu.field.access"
    _description = "Setu Field Access Description"

    name = fields.Char("Name")
    access_id = fields.Many2one(comodel_name="setu.access.rights")
    view_type = fields.Selection(selection=[('list', 'Tree'), ('form', 'Form')], string="View Type")

    model_id = fields.Many2one('ir.model', string='Model', index=True, required=True, ondelete="cascade")
    field_ids = fields.Many2many('ir.model.fields', 'setu_field_access_ir_model_fields_rel',
                                 'access_field_id', 'field_id', string='Fields')

    mode = fields.Selection(selection=[('invisible', 'Invisible'), ('readonly', 'Read Only'), ('required', 'Required')])

    @api.onchange('model_id')
    def _onchange_model_id(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 17/03/25
            Task: Migration from V16 to V18
            Purpose: It will clear the field value if we change the model name.
        """
        for rec in self:
            rec.field_ids = False
