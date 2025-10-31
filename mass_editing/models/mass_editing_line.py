# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
MAGIC_FIELDS = models.MAGIC_COLUMNS


class MassEditingLine(models.Model):
    _name = "mass.editing.line"
    _description = "Mass Editing Lines"
    _order = "sequence, field_id"

    sequence = fields.Integer()
    server_action_id = fields.Many2one(
        "ir.actions.server",
        string="Server Action",
        ondelete="cascade",
        required=True,
    )
    model_id = fields.Many2one(
        "ir.model",
        related="server_action_id.model_id",
    )
    # ("readonly", "!=", True),
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        domain=f"""
            [
                ("name", "not in", {str(MAGIC_FIELDS)}),
                ("ttype", "not in", ["reference", "function"]),
                ("model_id", "=", model_id),
            ]
        """,
        ondelete="cascade",
        required=True,
    )
    widget_option = fields.Char(
        help="Add widget text that will be used to display the field in the wizard.\n"
        "Example: 'many2many_tags', 'selection', 'image'",
    )
    apply_domain = fields.Boolean(
        default=False,
        help="Apply default domain related to field",
    )

    @api.constrains("server_action_id", "field_id")
    def _check_field_model(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: Check that all fields belong to the action model
        :return: None
        """
        if any(rec.field_id.model_id != rec.server_action_id.model_id for rec in self):
            raise ValidationError(
                _("Mass edit fields should belong to the server action model.")
            )

    @api.onchange("field_id")
    def _onchange_field_id(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 11/02/2025
        Task: [1571] Mass Editing (Migration)
        Purpose: This method will set widget option according to field
        :return: None
        """
        for rec in self:
            widget_option = False
            if rec.field_id.ttype == "many2many":
                widget_option = "many2many_tags"
            elif rec.field_id.ttype == "binary":
                if "image" in rec.field_id.name or "logo" in rec.field_id.name:
                    widget_option = "image"
            rec.widget_option = widget_option
