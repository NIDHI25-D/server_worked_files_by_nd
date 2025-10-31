from odoo import fields, models, api, _


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    partner_id = fields.Many2one('res.partner', string='Vendor')

    # def upload_xml_file(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Attach XML'),
    #         'res_model': 'attach.xml',
    #         'target': 'new',
    #         'view_id': self.env.ref('expenses_module_enhancement.attach_xml_wizard_form_view').id,
    #         'view_mode': 'form',
    #     }
    #
    # def _get_account_move_line_values(self):
    #     res = super(HrExpense, self)._get_account_move_line_values()
    #     current_journal = res.get(self.id)
    #     for line in current_journal:
    #         line['partner_id'] = self.partner_id.id if self.partner_id else False
    #     return res

    # def _prepare_move_line_vals(self):
    #     res = super(HrExpense, self)._prepare_move_line_vals()
    #     res.update({'partner_id': self.partner_id.id})
    #     return res


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    # def _prepare_bill_vals(self):
    #     res = super(HrExpenseSheet, self)._prepare_bill_vals()
    #     res.update({'partner_id': self.expense_line_ids.partner_id.id})
    #     return res

