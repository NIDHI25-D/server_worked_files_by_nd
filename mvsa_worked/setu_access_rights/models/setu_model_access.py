from odoo import fields, models, api, tools

class SetuModelAccess(models.Model):
    _name = "setu.model.access"
    _description = "Setu Model Access Description"

    name = fields.Char("Name")
    access_id = fields.Many2one(comodel_name="setu.access.rights")
    model_id = fields.Many2one('ir.model', string='Model', index=True, required=True, ondelete="cascade")
    restrict_create = fields.Boolean("Restrict Create")
    restrict_write = fields.Boolean("Restrict Edit")
    restrict_unlink = fields.Boolean("Restrict Delete")


class SetuReportsAccess(models.Model):
    _name = "setu.reports.access"
    _description = "Setu Reports Access Description"

    name = fields.Char("Name")
    access_id = fields.Many2one(comodel_name="setu.access.rights")
    model_id = fields.Many2one('ir.model', string='Model', index=True, required=True, ondelete="cascade")
    report_action_ids = fields.Many2many('ir.actions.report', 'ir_report_actions_setu_access_rel', 'raid', 'report_id',
                                         string='Reports')


class SetuActWindowAccess(models.Model):
    _name = "setu.act.window.access"
    _description = "Setu Act Window Access Description"

    name = fields.Char("Name")
    access_id = fields.Many2one(comodel_name="setu.access.rights")
    model_id = fields.Many2one('ir.model', string='Model', index=True, required=True, ondelete="cascade")
    act_action_ids = fields.Many2many('ir.actions.act_window', 'ir_act_actions_setu_access_rel', 'aaid', 'action_id',
                                      string='Actions')
