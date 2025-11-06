from odoo import models, api, tools, fields
from odoo.addons.base.models.ir_ui_menu import IrUiMenu
from odoo.osv import expression

base_load_menu = IrUiMenu.load_menus


@api.model
@tools.ormcache_context('self._uid', 'debug', keys=('lang',))
def load_menus(self, debug):
    """
      Author: jay.garach@setuconsulting.com
      Date: 17/03/25
      Task: Migration from V16 to V18
      Purpose: Loads all menu items (all applications and their submenus). With remove the menu items that are present
                    into the setu access rights record.
    """
    try:
        self.env['setu.access.rights']
    except KeyError:
        return base_load_menu(self=self, debug=debug)
    fields = ['name', 'sequence', 'parent_id', 'action', 'web_icon']
    menu_roots = self.get_user_roots()
    menu_roots_data = menu_roots.read(fields) if menu_roots else []
    menu_root = {
        'id': False,
        'name': 'root',
        'parent_id': [-1, ''],
        'children': [menu['id'] for menu in menu_roots_data],
    }

    all_menus = {'root': menu_root}

    if not menu_roots_data:
        return all_menus

    # menus are loaded fully unlike a regular tree view, cause there are a
    # limited number of items (752 when all 6.1 addons are installed)
    menus_domain = [('id', 'child_of', menu_roots.ids)]
    blacklisted_menu_ids = self._load_menus_blacklist()
    if blacklisted_menu_ids:
        menus_domain = expression.AND([menus_domain, [('id', 'not in', blacklisted_menu_ids)]])
    menus = self.search(menus_domain)

    # ***************************************** Custom Changes *****************************************
    all_searched_menu = self.env['setu.access.rights'].search(
        ['|', ('user_ids', '=', self._uid), '&', ('use_exclude_users_ids_field', '=', True),
         ('exclude_user_ids', '!=', self._uid)]).mapped('menu_access_ids')
    if menus and all_searched_menu:
        menu_ids = all_searched_menu.mapped('menu_ids').ids
        blocked_menu_contains_settings = [blocked_menu for blocked_menu in all_searched_menu.mapped('menu_ids') if
                                          blocked_menu.display_name == "Settings"]
        if blocked_menu_contains_settings:
            remove_menus = menus.filtered(lambda
                                              m: m.name.lower() == "Settings".lower() and m.parent_id and "configuration".lower() in m.parent_id.complete_name.lower())
            menus = menus.filtered(lambda m: m.id not in remove_menus.mapped('id'))
        else:
            menus = menus.filtered(lambda m: m.id not in menu_ids)
    # **************************************************************************************************

    menu_items = menus.read(fields)
    xmlids = (menu_roots + menus)._get_menuitems_xmlids()

    # add roots at the end of the sequence, so that they will overwrite
    # equivalent menu items from full menu read when put into id:item
    # mapping, resulting in children being correctly set on the roots.
    menu_items.extend(menu_roots_data)

    mi_attachments = self.env['ir.attachment'].sudo().search_read(
        domain=[('res_model', '=', 'ir.ui.menu'),
                ('res_id', 'in', [menu_item['id'] for menu_item in menu_items if menu_item['id']]),
                ('res_field', '=', 'web_icon_data')],
        fields=['res_id', 'datas', 'mimetype'])

    mi_attachment_by_res_id = {attachment['res_id']: attachment for attachment in mi_attachments}

    # set children ids and xmlids
    menu_items_map = {menu_item["id"]: menu_item for menu_item in menu_items}
    for menu_item in menu_items:
        menu_item.setdefault('children', [])
        parent = menu_item['parent_id'] and menu_item['parent_id'][0]
        menu_item['xmlid'] = xmlids.get(menu_item['id'], "")
        if parent in menu_items_map:
            menu_items_map[parent].setdefault(
                'children', []).append(menu_item['id'])
        attachment = mi_attachment_by_res_id.get(menu_item['id'])
        if attachment:
            menu_item['web_icon_data'] = attachment['datas'].decode()
            menu_item['web_icon_data_mimetype'] = attachment['mimetype']
        else:
            menu_item['web_icon_data'] = False
            menu_item['web_icon_data_mimetype'] = False
    all_menus.update(menu_items_map)

    # sort by sequence
    for menu_id in all_menus:
        all_menus[menu_id]['children'].sort(key=lambda id: all_menus[id]['sequence'])

    # recursively set app ids to related children
    def _set_app_id(app_id, menu):
        menu['app_id'] = app_id
        for child_id in menu['children']:
            _set_app_id(app_id, all_menus[child_id])

    for app in menu_roots_data:
        app_id = app['id']
        _set_app_id(app_id, all_menus[app_id])

    # filter out menus not related to an app (+ keep root menu)
    all_menus = {menu['id']: menu for menu in all_menus.values() if menu.get('app_id')}
    all_menus['root'] = menu_root

    return all_menus


IrUiMenu.load_menus = load_menus


class Menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        """
            Authour:yash@setconsulting
            Date: 13/02/23
            Task: 16 Migration
            Purpose: Return the ids of the menu items visible to the user.
                Also, it will exclude the menu items that are present into the setu access right's records.
        """
        menus = super(Menu, self)._visible_menu_ids(debug)
        menu_ids = self.env['setu.access.rights'].search(
            ['|', ('user_ids', '=', self._uid), '&', ('use_exclude_users_ids_field', '=', True),
             ('exclude_user_ids', '!=', self._uid)]).mapped('menu_access_ids')
        if menu_ids:
            for rec in menu_ids.mapped('menu_ids').ids:
                menus.discard(rec)
        return menus
