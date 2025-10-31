from odoo import fields, models, api


class SetuAccessRights(models.Model):
    _name = "setu.access.rights"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Setu Access Management"

    name = fields.Char("Access Right Name", required=True, tracking=True)
    user_ids = fields.Many2many('res.users', 'setu_access_rights_users_rel',
                                'access_right_id', 'user_id', string='Users')
    disable_chatter = fields.Boolean("Remove chatter")
    remove_create_contextual_action_button = fields.Boolean("Remove Create contextual action from the Server action")
    fields_access_ids = fields.One2many(comodel_name='setu.field.access', inverse_name="access_id")
    model_access_ids = fields.One2many(comodel_name='setu.model.access', inverse_name="access_id")
    menu_access_ids = fields.One2many(comodel_name='setu.menu.access', inverse_name="access_id")
    reports_access_ids = fields.One2many(comodel_name='setu.reports.access', inverse_name="access_id")
    act_window_access_ids = fields.One2many(comodel_name='setu.act.window.access', inverse_name="access_id")
    exclude_user_ids = fields.Many2many('res.users', 'setu_access_rights_exclude_users_rel',
                                        'access_right_id', 'user_id', string="Exclude users")
    use_exclude_users_ids_field = fields.Boolean(string="Use Exclude User field")
    notebook_access_ids = fields.One2many(comodel_name='setu.notebook.access', inverse_name='access_id')
    active = fields.Boolean(default=True)

    @api.onchange('use_exclude_users_ids_field')
    def onchange_method_for_use_exclude_users_ids_field(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 17/03/25
            Task: Migration from V16 to V18
            Purpose: It will clear the user fields according to change the use_exclude_users_ids_field fields
        """
        self.user_ids = False
        self.exclude_user_ids = False

    def write(self, vals):
        res = super(SetuAccessRights, self).write(vals)
        self.clear_caches()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SetuAccessRights, self).create(vals_list)
        self.clear_caches()
        return res

    def unlink(self):
        res = super(SetuAccessRights, self).unlink()
        self.clear_caches()
        return res
