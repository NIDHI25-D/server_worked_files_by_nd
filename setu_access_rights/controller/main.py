from odoo.addons.web.controllers.action import Action
from odoo.http import request, route


class ActionCustom(Action):

    @route('/web/action/load', type='json', auth='user', readonly=True)
    def load(self, action_id, context=None):
        res = super(ActionCustom, self).load(action_id, context)
        # Your code goes here
        act_type = res.get('type', False)
        if res.get('res_model') != 'setu.access.rights' and act_type:
            menu_ids = request.env['setu.access.rights'].search(
                ['|', ('user_ids', '=', request.uid), '&', ('use_exclude_users_ids_field', '=', True),
                 ('exclude_user_ids', '!=', request.uid)]).mapped(
                'menu_access_ids').mapped('all_menu_ids').filtered(
                lambda x: x.action and x.action.sudo().type == act_type)
            if menu_ids and res.get('id') in [i.id for i in menu_ids.mapped('action')]:
                res = ""
        return res
