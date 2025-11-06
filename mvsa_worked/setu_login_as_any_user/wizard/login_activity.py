from odoo import api, fields, models
from odoo.http import request
import time

class ResUsersApikeysDescription(models.TransientModel):
    _inherit = "res.users.apikeys.description"

    def check_access_make_key(self):
        if self._context.get('allow_to_generate'):
            return True
        return super(ResUsersApikeysDescription, self).check_access_make_key()


class LoginActivity(models.TransientModel):
    _name = 'login.activity'
    _description = 'Login Activity'

    user_id = fields.Many2one('res.users')
    group_ids = fields.Many2many('res.groups', string='Groups', related='user_id.groups_id')

    def login_to_user(self):
        request.session['identity-check-last'] = time.time() + 20 * 60
        request.session.pre_login = self.env.user.login
        request.session.pre_uid = self.env.user.id
        res = self.env['res.users.apikeys.description'].with_user(self.user_id.id).create({'name': 'temp_login'})
        res = res.with_context(allow_to_generate=True).make_key().get('context', {}).get('default_key')
        self._cr.commit()
        credentials={'login': self.user_id.login, 'password': res, 'type': 'password'}
        uid = self.user_id.sudo().authenticate(self._cr.dbname, credentials, {'interactive': False})
        # uid = self.user_id.sudo().authenticate(self._cr.dbname, self.user_id.login, res)
        request.session.finalize(self.env)
        request.session.uid = uid.get('uid', False)
        request.update_env(user=uid.get('uid', False))
        request.update_context(**request.session.context)
        self._cr.execute(f"DELETE FROM res_users_apikeys where index='{res[:8]}'")
        request.params['login_success'] = True
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
