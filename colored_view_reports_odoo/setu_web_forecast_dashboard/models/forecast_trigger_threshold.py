from odoo import models, fields, api,_
from odoo.tools.safe_eval import safe_eval
from odoo.tools import float_compare, float_round
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class TriggerThreshold(models.Model):
    _name = 'trigger.threshold'
    _description = 'Trigger Threshold Line'

    trigger_id = fields.Many2one('trigger.main', string='Main Trigger')
    sequence = fields.Integer(string="Number")
    threshold_name = fields.Char(string='Threshold Name')  # e.g., '30d DOI ≤ 120'
    threshold_parent_domain = fields.Char(string="Threshold Parent Domain")

    # Conditions
    condition_type_forecast = fields.Selection([
        ('rules', "Rules"),
        ('rules_by_domain', "Rules by Domain"),
    ], string="Condition type Forecast")

    threshold_domain = fields.Char(string="Threshold Domain")
    threshold_line_ids = fields.One2many(
        'trigger.threshold.line',
        'threshold_id',
        string="Rule Lines"
    )
    is_applied = fields.Boolean(string="Applied", default=False)


    def action_open_threshold_line_form(self):
        # This will open rules form from the threshold_line_ids by clicking on Edit
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Threshold Line Details',
            'res_model': 'trigger.threshold',
            'view_mode': 'form',
            'views': [
                (self.env.ref('setu_web_forecast_dashboard.view_trigger_threshold_popup_form').id, 'form')
            ],
            'res_id': self.id,
            'target': 'current',  # or 'new' for popup
        }

    @api.constrains('threshold_line_ids')
    def _check_logical_operator_sequence(self):
        """
        Rule:
        - Every line except the last one must have a Logical Operator (AND/OR)
        - The last line must NOT have a Logical Operator
        """
        for record in self:
            lines = record.threshold_line_ids.sorted('sequence')
            if not lines:
                continue

            for idx, line in enumerate(lines):
                is_last = (idx == len(lines) - 1)
                # 🔸 For all lines except the last → must have logical
                if not is_last and not line.logical:
                    raise ValidationError(_(
                        "A Line in '%s' is missing a Logical Operator (AND/OR) "
                        "before creating the next rule."
                    ) % (record.threshold_name or record.display_name))
                # 🔸 For last line → must NOT have logical
                if is_last and line.logical:
                    raise ValidationError(_(
                        "The last rule line in '%s' should not have a Logical Operator. "
                        "Either remove it or add another rule below."
                    ) % (record.threshold_name or record.display_name))

            _logger.info(
                "✅ Logical validation passed for Threshold '%s' with %d lines",
                record.threshold_name, len(lines)
            )
