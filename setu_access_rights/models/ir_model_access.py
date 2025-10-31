from odoo import fields, models, api, tools


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context('self._uid', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        """
            Author: jay.garach@setuconsulting.com
            Date: 17/03/25
            Task: Migration from V16 to V18
            Purpose: Verify that the given operation is allowed for the current user accord to ir.model.access
        """
        if self._uid == 1 or self._context.get('bypass_access', False):
            return True

        if mode != 'read':
            access_ids = self.env['setu.access.rights'].with_context(bypass_access=True).search(
                ['|',
                 ('user_ids', '=', self._uid), '&', ('use_exclude_users_ids_field', '=', True),
                 ('exclude_user_ids', '!=', self._uid)])
            model_access_ids = access_ids.mapped('model_access_ids').filtered(
                lambda x: x.model_id.model == model)
            if model_access_ids:
                if any(model_access_ids.mapped('restrict_{}'.format(mode))):
                    return False
        return super(IrModelAccess, self).check(model, mode, raise_exception)
