from odoo import models, fields, api, _

class CrmActionType(models.Model):
    _name = "crm.action.type"
    _description = "Action Type"

    name = fields.Char(string="Name", required=True, translate=True)
    crm_case_categ_id = fields.Many2one('crm.case.categ', string="Category")
