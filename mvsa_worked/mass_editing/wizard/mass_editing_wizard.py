# -*- coding: utf-8 -*-
import json
from lxml import etree
from odoo import _, api, fields, models


class MassEditingWizard(models.TransientModel):
    _name = "mass.editing.wizard"
    _description = "Wizard for mass edition"

    selected_item_qty = fields.Integer(readonly=True)
    remaining_item_qty = fields.Integer(readonly=True)
    operation_description_info = fields.Text(readonly=True)
    operation_description_warning = fields.Text(readonly=True)
    operation_description_danger = fields.Text(readonly=True)
    message = fields.Text(readonly=True)

    @api.model
    def default_get(self, fields):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: Set default values
        :param fields: 
        :return: dictionary
        """
        res = super().default_get(fields)
        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        active_ids = self.env.context.get("active_ids")

        if not server_action:
            return res

        original_active_ids = self.env.context.get("original_active_ids", active_ids)
        operation_description_info = False
        operation_description_warning = False
        operation_description_danger = False
        if len(active_ids) == len(original_active_ids):
            operation_description_info = _(
                "The treatment will be processed on the %(amount)d selected record(s)."
            ) % {
                "amount": len(active_ids),
            }
        elif len(original_active_ids):
            operation_description_warning = _(
                "You have selected %(origin_amount)d "
                "record(s) that can not be processed.\n"
                "Only %(amount)d record(s) will be processed."
            ) % {
                "origin_amount": len(original_active_ids) - len(active_ids),
                "amount": len(active_ids),
            }
        else:
            operation_description_danger = _(
                "None of the %(amount)d record(s) you have selected can be processed."
            ) % {
                "amount": len(active_ids),
            }
        # Set values
        res.update(
            {
                "selected_item_qty": len(active_ids),
                "remaining_item_qty": len(original_active_ids),
                "operation_description_info": operation_description_info,
                "operation_description_warning": operation_description_warning,
                "operation_description_danger": operation_description_danger,
                "message": server_action.mass_edit_message,
            }
        )

        return res

    def onchange(self, values, field_names, fields_spec):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: This method will used to dynamic field
        :param values:
        :param field_names:
        :param fields_spec:
        :return: dictionary
        """
        first_call = not field_names
        if first_call:
            field_names = [fname for fname in values if fname != "id"]
            missing_names = [fname for fname in fields_spec if fname not in values]
            defaults = self.default_get(missing_names)
            for field_name in missing_names:
                values[field_name] = defaults.get(field_name, False)
                if field_name in defaults:
                    field_names.append(field_name)
                    
        # This section was written by the test case of the task : https://app.clickup.com/t/86dx2br60 { Server Action Issue D}
        # In this,Server action : Update - Analytic Account in which field: analytic_distribution,widget: analytic_distribution. While adding action to the Journal Items it used to give error: keyError --'analytic_precision' which was appearing when doing for the field:analytic_distribution
        field_names = [f for f in field_names if f in self._fields]
        values = {k: v for k, v in values.items() if k in self._fields}
        fields_spec = {k: v for k, v in fields_spec.items() if k in self._fields}

        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        if not server_action:
            return super().onchange(values, field_names, fields_spec)
        dynamic_fields = {}

        for line in server_action.mapped("mass_edit_line_ids"):
            values["selection__" + line.field_id.name] = "ignore"
            values[line.field_id.name] = False

            dynamic_fields["selection__" + line.field_id.name] = fields.Selection(
                [], default="ignore"
            )

            dynamic_fields[line.field_id.name] = fields.Text([()], default=False)

        self._fields.update(dynamic_fields)

        res = super().onchange(values, field_names, fields_spec)
        if not res["value"]:
            value = {key: value for key, value in values.items() if value is not False}
            res["value"] = value

        for field in dynamic_fields:
            self._fields.pop(field)

        view_temp = (
            self.env["ir.ui.view"]
            .sudo()
            .search([("name", "=", "Temporary Mass Editing Wizard")], limit=1)
        )
        if view_temp:
            view_temp.unlink()

        return res

    @api.model
    def _prepare_fields(self, line, field, field_info):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: This method will used to prepare fields
        :param line:
        :param field:
        :param field_info:
        :return: dictionary
        """
        result = {}
        # Add "selection field (set / add / remove / remove_m2m)
        if field.ttype == "many2many":
            selection = [
                ("ignore", _("Don't touch")),
                ("set_m2m", _("Set")),
                ("remove_m2m", _("Remove")),
                ("add", _("Add")),
            ]
        elif field.ttype == "one2many":
            selection = [
                ("ignore", _("Don't touch")),
                ("set_o2m", _("Set")),
                ("add_o2m", _("Add")),
            ]
        else:
            selection = [
                ("ignore", _("Don't touch")),
                ("set", _("Set")),
                ("remove", _("Remove")),
            ]
        result["selection__" + field.name] = {
            "type": "selection",
            "string": field_info["string"],
            "selection": selection,
        }
        # Add field info
        result[field.name] = field_info
        return result

    @api.model
    def _insert_field_in_arch(self, line, field, main_xml_group):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: This method will used to insert field in wizard view architecture
        :param line:
        :param field:
        :param main_xml_group:
        :return: field element object
        """
        etree.SubElement(
            main_xml_group,
            "label",
            {
                "for": "selection__" + field.name,
            },
        )
        div = etree.SubElement(
            main_xml_group,
            "div",
            {
                "class": "d-flex",
            },
        )
        etree.SubElement(
            div,
            "field",
            {
                "name": "selection__" + field.name,
                "required": '1',
                "class": "w-25",
            },
        )
        field_vals = self._get_field_options(field)
        if line.widget_option:
            field_vals["widget"] = line.widget_option
        field_element = etree.SubElement(div, "field", field_vals)
        if field.ttype == "one2many":
            comodel = self.env[field.relation]
            dummy, form_view = comodel._get_view(view_type="form")
            dummy, list_view = comodel._get_view(view_type="list")
            field_context = {}
            if form_view:
                field_context["form_view_ref"] = form_view.xml_id
            if list_view:
                field_context["list_view_ref"] = list_view.xml_id
            if field_context:
                field_element.attrib["context"] = json.dumps(field_context)
            else:
                model_arch, dummy = self.env[field.model]._get_view(view_type="form")
                embedded_list = None
                for node in model_arch.xpath(f"//field[@name='{field.name}'][./list]"):
                    embedded_list = node.xpath("./list")[0]
                    break
                if embedded_list is not None:
                    for node in embedded_list.xpath("./*"):
                        modifiers = node.get("modifiers")
                        if modifiers:
                            node.attrib["modifiers"] = modifiers
                    field_element.insert(0, embedded_list)

        return field_element

    def _get_field_options(self, field):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: This method will used to pass fields attribute
        :param field: 
        :return: dictonary 
        """
        return {
            "name": field.name,
            "invisible": f'selection__{field.name} in ["ignore", "remove", False]',
            "class": "w-75",
            "readonly": '0',
        }

    @api.model
    def get_views(self, views, options=None):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: The get views method returns the field_views of given view. Before get view call we set server action in view and pass context
        :param views: view id and view mode
        :param options: dictionary
        :return: dictionary
        """
        for view, _type in views:
            if view:
                view = self.env["ir.ui.view"].sudo().browse(view)
                server_action = view.mass_server_action_id
                self = self.with_context(server_action_id=server_action.id)
        return super().get_views(views, options)

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: This method will used to update view architecture
        :param view_id: 
        :param view_type: 
        :param options: 
        :return: dictionary
        """
        view = self.env["ir.ui.view"].sudo().browse(view_id)
        server_action = view.mass_server_action_id
        self = self.with_context(server_action_id=server_action.id)
        if not server_action:
            return super().get_view(view_id, view_type, **options)
        result = super().get_view(view_id, view_type, **options)
        arch = etree.fromstring(result["arch"])
        main_xml_group = arch.find('.//group[@name="group_field_list"]')
        for line in server_action.mapped("mass_edit_line_ids"):
            self._insert_field_in_arch(line, line.field_id, main_xml_group)
            if line.field_id.ttype == "one2many":
                comodel = self.env[line.field_id.relation]
                result["models"] = dict(
                    result["models"], **{comodel._name: tuple(comodel.fields_get())}
                )
        result["arch"] = etree.tostring(arch, encoding="unicode")
        return result

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: The field_get use get fields details. 
                 Added new field on wizard which configured in server action.
        :param allfields: 
        :param attributes: 
        :return: field dictionary 
        """
        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        if not server_action:
            return super().fields_get(allfields, attributes)
        res = super().fields_get(allfields, attributes)
        fields_info = self.env[server_action.model_id.model].fields_get()
        for line in server_action.mapped("mass_edit_line_ids"):
            field = line.field_id
            field_info = self._clean_check_company_field_domain(
                self.env[server_action.model_id.model], field, fields_info[field.name]
            )
            field_info["relation_field"] = False
            if not line.apply_domain and "domain" in field_info:
                field_info["domain"] = "[]"
            res.update(self._prepare_fields(line, field, field_info))
        return res

    @api.model
    def _clean_check_company_field_domain(self, TargetModel, field, field_info):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: This method remove the field view domain added by Odoo for relational
                 fields with check_company attribute to avoid error for non exists
                 company_id or company_ids fields in wizard view.
                 See _description_domain method in _Relational Class
        :param TargetModel: 
        :param field: 
        :param field_info: 
        :return: 
        """
        field_class = TargetModel._fields[field.name]
        if not field_class.relational or not field_class.check_company or field.domain:
            return field_info
        field_info["domain"] = "[]"
        return field_info

    @api.model_create_multi
    def create(self, vals_list):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: This method will used to prepare dictionary{'field', value} which field do you want to update in active ids
        :param vals_list: 7
        :return: recordset
        """
        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        active_ids = self.env.context.get("active_ids", [])
        if server_action and active_ids:
            for vals in vals_list:
                values = {}
                for key, val in vals.items():
                    if key.startswith("selection_"):
                        split_key = key.split("__", 1)[1]
                        if val == "set" or val == "add_o2m":
                            values.update({split_key: vals.get(split_key, False)})

                        elif val == "set_o2m" or val == "set_m2m":
                            values.update(
                                {split_key: [(6, 0, [])] + vals.get(split_key, [])}
                            )

                        elif val == "remove":
                            values.update({split_key: False})

                        elif val == "remove_m2m":
                            m2m_list = []
                            if vals.get(split_key):
                                for m2m_id in vals.get(split_key, False):
                                    m2m_list.append((3, m2m_id[1]))
                            if m2m_list:
                                values.update({split_key: m2m_list})
                            else:
                                values.update({split_key: [(5, 0, [])]})

                        elif val == "add":
                            values.update({split_key: vals.get(split_key, False)})

                if values:
                    for active_id in active_ids:
                        self.env[server_action.model_id.model].browse(
                            active_id
                        ).with_context(
                            mass_edit=True,
                        ).write(values)
        return super().create([{}])

    def _prepare_create_values(self, vals_list):
        return vals_list

    def read(self, fields=None, load="_classic_read"):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: Without this call, dynamic fields build by fields_view_get()
                generate a log warning, i.e.:
                odoo.models:mass.editing.wizard.read() with unknown field 'myfield'
                odoo.models:mass.editing.wizard.read()
                    with unknown field 'selection__myfield'
        :param fields: 
        :param load: 
        :return: list of dictionary
        """
        real_fields = fields
        if fields:
            # We remove fields which are not in _fields
            real_fields = [x for x in fields if x in self._fields]
        result = super().read(real_fields, load=load)
        # adding fields to result
        [result[0].update({x: False}) for x in fields if x not in real_fields]
        return result

    def button_apply(self):
        self.ensure_one()
