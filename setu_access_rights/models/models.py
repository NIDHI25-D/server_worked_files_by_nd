from odoo import api, models, _
import itertools
from lxml import etree

from odoo.addons.base.models.ir_ui_view import Model

base_get_views = Model.get_views


@api.model
def get_views(self, views, options=None):
    """
      Author: jay.garach@setuconsulting.com
      Date: 17/03/25
      Task: Migration from V16 to V18
      Purpose: Get the detailed composition of the requested view like fields, model, view architecture
    """
    try:
        self.env['setu.access.rights']
    except KeyError:
        return base_get_views(self, views, options=None)
    # *BASE USE*
    options = options or {}
    result = {}

    # Getting the all views for model like list,form and all.
    result['views'] = {
        v_type: self.get_view(
            v_id, v_type,
            **options
        )
        for [v_id, v_type] in views
    }

    # setting default model and model fields.
    models = {}
    for view in result['views'].values():
        for model, model_fields in view.pop('models').items():
            models.setdefault(model, set()).update(model_fields)

    result['models'] = {}

    # setting the model into result.
    for model, model_fields in models.items():
        result['models'][model] = {"fields": self.env[model].fields_get(
            allfields=model_fields, attributes=self._get_view_field_attributes()
        )}
    # *BASE USE*

    # ********************************************************
    access_ids = self.env['setu.access.rights'].search(
        ['|', ('user_ids', '=', self._uid), '&', ('use_exclude_users_ids_field', '=', True),
         ('exclude_user_ids', '!=', self._uid)])

    # Find the one2Many type fields of current model which is not related with it self.
    models_of_one2many_field_of_current_model = self.env['ir.model.fields'].search(
        [('model_id.model', '=', self._name), ('ttype', '=', 'one2many'), ('relation', '!=', self._name)]).mapped(
        'relation')
    # append the current model into the one2Many list
    to_find_fields = models_of_one2many_field_of_current_model.copy()
    to_find_fields.append(self._name)
    # ******************************************************

    # Add related action information if asked
    if options.get('toolbar'):
        for view in result['views'].values():
            view['toolbar'] = {}

        bindings = self.env['ir.actions.actions'].get_bindings(self._name)
        # ************************* result['views'][view_type]['toolbar'] LOOPS
        # Don't see the use of string key that is set here
        if bindings.get('report') and bindings.get('action'):
            for res in itertools.chain(bindings.get('report'), bindings.get('action')):
                res['string'] = res['name']
        # *************************

        # *BASE USE*
        if options.get('load_filters') and 'search' in result['views']:
            result['views']['search']['filters'] = self.env['ir.filters'].get_filters(
                self._name, options.get('action_id'), options.get('embedded_action_id'),
                options.get('embedded_parent_res_id')
            )
        # *BASE USE*

        # ********************************************************
        # For Report
        reports_access_ids = access_ids.mapped('reports_access_ids').filtered(lambda x: x.model_id.model == self._name)
        reports = reports_access_ids.mapped('report_action_ids').mapped('name')

        # For Action Windows
        act_window_access_ids = access_ids.mapped('act_window_access_ids').filtered(
            lambda x: x.model_id.model == self._name)
        act_actions = act_window_access_ids.mapped('act_action_ids').mapped('name')

        if bindings.get('report') and bindings.get('action'):
            # don't know the purpose to use temp_resreport when it's iterating bindings report object
            temp_resreport = bindings.get('report').copy()

            # If found any access right related to the report and action, then it will remove from the bindings (that are load from get from the base)
            if reports:
                for report in temp_resreport:
                    if report.get('name', False) in reports:
                        index = bindings.get('report').index(report)
                        bindings.get('report').pop(index)

            if act_actions:
                for action in bindings.get('action'):
                    if action.get('name', False) in act_actions:
                        index = bindings.get('action').index(action)
                        bindings.get('action').pop(index)

        for action_type, key in (('report', 'print'), ('action', 'action')):
            for action in bindings.get(action_type, []):
                view_types = (
                    action['binding_view_types'].split(',')
                    if action.get('binding_view_types')
                    else result['views'].keys()
                )
                for view_type in view_types:
                    if view_type in result['views']:
                        result['views'][view_type]['toolbar'].setdefault(key, []).append(action)

    fields_access_ids = access_ids.mapped('fields_access_ids').filtered(lambda m: m.model_id.model in to_find_fields)

    parser = etree.XMLParser(remove_blank_text=True)

    active_view_types = list(result['views'].keys())
    for fields_access_id in fields_access_ids.filtered(lambda v: v.view_type in ['form', 'list', 'tree']):
        if fields_access_id.mode:
            for field in fields_access_id.field_ids:

                """
                Execute if field of access rights record is present in one2Many fields(views)
                Ex. if you are opening sale order and create an acces rights record for the fields of sale order line then it will be excecuted.
                """
                if fields_access_id.model_id.model in models_of_one2many_field_of_current_model:
                    field_to_find_in_xml = self.env['ir.model.fields'].search(
                        [('model_id.model', '=', self._name), ('ttype', '=', 'one2many'),
                         ('relation', '=', fields_access_id.model_id.model)]).mapped('name')
                    if field_to_find_in_xml and field_to_find_in_xml[0] in result['models'][self._name][
                        'fields'].keys():
                        if result.get('views'):
                            if result.get('views').get('form'):
                                temp_form = etree.fromstring(
                                    result.get('views').get('form')['arch'],
                                    parser=parser)
                                for node in temp_form.xpath(f"//*[@name='{field.name}']"):
                                    if len([a for a in
                                            node.iterancestors('list')]) > 0 and fields_access_id.mode == 'invisible':
                                        node.attrib['column_invisible'] = '1'
                                    elif len([a for a in node.iterancestors('list')]) > 0:
                                        node.attrib[f'{fields_access_id.mode}'] = '1'

                                result.get('views').get('form')['arch'] = etree.tostring(
                                    temp_form)
                            if result.get('views').get('list'):
                                temp_tree = etree.fromstring(
                                    result.get('views').get('list').get('arch'),
                                    parser=parser)
                                for node in temp_tree.xpath("//field[@name='{}']".format(field.name)):
                                    node.attrib['column_invisible'] = '1'
                                    node.attrib[f'{fields_access_id.mode}'] = '1'

                                for node in temp_tree.xpath("//label[@for='{}']".format(field.name)):
                                    if fields_access_id.mode == 'invisible':
                                        node.set("style", "display: none")
                                        node.attrib[f'{fields_access_id.mode}'] = '1'

                                result.get('views').get('list')['arch'] = etree.tostring(
                                    temp_tree)
                else:
                    """
                    It will be executed if access rights records fields is normal type likes Char,integer Float etc.....
                    """
                    arch = result.get('views', {}).get(fields_access_id.view_type, {}).get('arch')
                    if not arch:
                        continue
                    temp_view_arch = etree.fromstring(arch, parser=parser)
                    if fields_access_id.model_id.model in result.get('models').keys():
                        for node in temp_view_arch.xpath(f"//*[@name='{field.name}']"):
                            if fields_access_id.mode == 'invisible':
                                if fields_access_id.view_type in ['tree', 'list']:
                                    node.attrib['column_invisible'] = '1'
                                else:
                                    node.attrib[f'{fields_access_id.mode}'] = '1'
                            elif fields_access_id.mode == 'readonly':
                                node.attrib[f'{fields_access_id.mode}'] = '1'
                                node.attrib['force_save'] = '1'
                            else:
                                node.attrib[f'{fields_access_id.mode}'] = '1'
                        for node in temp_view_arch.xpath(f"//*[@for='{field.name}']"):
                            if fields_access_id.mode == 'invisible':
                                if fields_access_id.view_type in ['tree', 'list']:
                                    node.attrib['column_invisible'] = '1'
                                else:
                                    node.attrib[f'{fields_access_id.mode}'] = '1'
                            elif fields_access_id.mode == 'readonly':
                                node.attrib[f'{fields_access_id.mode}'] = '1'
                                node.attrib['force_save'] = '1'
                            else:
                                node.attrib[f'{fields_access_id.mode}'] = '1'

                    result.get('views').get(fields_access_id.view_type).update({'arch': etree.tostring(temp_view_arch)})

    # Removing chatter from record view
    if 'form' in active_view_types and any(access_ids.mapped('disable_chatter')):
        parser = etree.XMLParser(remove_blank_text=True)
        arch = etree.fromstring(result.get('views').get('form').get('arch'), parser=parser)
        chatters = arch.xpath("//chatter")
        for chatter in chatters:
            arch.remove(chatter)
        result.get('views').get('form').update({'arch': etree.tostring(arch)})

    # Removing contextual action button from server action.
    if 'form' in active_view_types and any(
            access_ids.mapped('remove_create_contextual_action_button')) and self._name == "ir.actions.server":
        parser = etree.XMLParser(remove_blank_text=True)
        arch = etree.fromstring(result.get('views').get('form').get('arch'), parser=parser)
        contextual_action = arch.xpath("//button[@name='create_action']")
        for node in contextual_action:
            node.attrib['invisible'] = '1'
        result.get('views').get('form').update({'arch': etree.tostring(arch)})

    # For Notebook
    notebook_access_ids = access_ids.notebook_access_ids.filtered(lambda x: x.model_id.model == self._name)
    for nb_access_line in notebook_access_ids:
        if result.get('views').get('form'):
            notebook_structure = etree.fromstring(
                result.get('views').get('form').get('arch'),
                parser=parser)
            for nb_field in nb_access_line.field_ids:
                for node in notebook_structure.xpath(f"//field[@name='{nb_field.name}']/.."):
                    node.attrib[f'{notebook_access_ids.mode}'] = '1'
            result.get('views').get('form').update({'arch': etree.tostring(notebook_structure)})
    return result


Model.get_views = get_views
