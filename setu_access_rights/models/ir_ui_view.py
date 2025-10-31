from odoo.addons.base.models.ir_ui_view import View
from odoo.http import request
import functools

base_postprocess_access_rights = View._postprocess_access_rights


def _postprocess_access_rights(self, tree):
    """ Apply group restrictions: elements with a 'groups' attribute should
    be made invisible to people who are not members.
    """
    """
      Author: jay.garach@setuconsulting.com
      Date: 17/03/25
      Task: Migration from V16 to V18
      Purpose: Apply group restrictions: elements with a 'groups' attribute should
        be removed from the view to people who are not members.

        Compute and set on node access rights based on view type. Specific
        views can add additional specific rights like creating columns for
        many2one-based grouping views.
        
        Also It will remove the  menu from the settings which is selected in Setu access record 
    """
    try:
        self.env['setu.access.rights']
    except KeyError:
        return base_postprocess_access_rights(self, tree)
    access_ids = self.env['setu.access.rights'].search(
        ['|', ('user_ids', '=', self._uid), '&', ('use_exclude_users_ids_field', '=', True),
         ('exclude_user_ids', '!=', self._uid)])
    menu_access_blocked = access_ids.menu_access_ids.menu_ids.mapped('display_name')

    # AS PER BASE V18
    group_definitions = self.env['res.groups']._get_group_definitions()

    user_group_ids = self.env.user._get_group_ids()
    # The 'base.group_no_one' is not actually involved by any other group because it is session dependent.
    group_no_one_id = group_definitions.get_id('base.group_no_one')
    if group_no_one_id in user_group_ids and not (request and request.session.debug):
        user_group_ids = [g for g in user_group_ids if g != group_no_one_id]

    # check the read/visibility access
    @functools.cache
    def has_access(groups_key):
        groups = group_definitions.from_key(groups_key)
        return groups.matches(user_group_ids)

    # check the read/visibility access
    for node in tree.xpath('//*[@__groups_key__]'):
        if node.attrib.get('string') in menu_access_blocked:
            node.attrib['invisible'] = '1'

        if not has_access(node.attrib.pop('__groups_key__')):
            node.getparent().remove(node)
        elif node.tag == 't' and not node.attrib:
            # Move content of <t groups=""> blocks
            # and remove the <t> node.
            # This is to keep the structure
            # <group>
            #   <field name="foo"/>
            #   <field name="bar"/>
            # <group>
            # so the web client adds the label as expected.
            # This is also to avoid having <t> nodes in list views
            # e.g.
            # <list>
            #   <field name="foo"/>
            #   <t groups="foo">
            #     <field name="bar" groups="bar"/>
            #   </t>
            # </list>
            for child in reversed(node):
                node.addnext(child)
            node.getparent().remove(node)

    # check the create and write access
    base_model = tree.get('model_access_rights')
    for node in tree.xpath('//*[@model_access_rights]'):
        model = self.env[node.attrib.pop('model_access_rights')]
        if node.tag == 'field':
            can_create = model.has_access('create')
            can_write = model.has_access('write')
            node.set('can_create', str(bool(can_create)))
            node.set('can_write', str(bool(can_write)))
        else:
            is_base_model = base_model == model._name
            for action, operation in (('create', 'create'), ('delete', 'unlink'), ('edit', 'write')):
                if not node.get(action) and not model.has_access(operation):
                    node.set(action, 'False')
            if node.tag == 'kanban':
                group_by_name = node.get('default_group_by')
                group_by_field = model._fields.get(group_by_name)
                if group_by_field and group_by_field.type == 'many2one':
                    group_by_model = model.env[group_by_field.comodel_name]
                    for action, operation in (
                            ('group_create', 'create'), ('group_delete', 'unlink'), ('group_edit', 'write')):
                        if not node.get(action) and not group_by_model.has_access(operation):
                            node.set(action, 'False')

    return tree


View._postprocess_access_rights = _postprocess_access_rights
