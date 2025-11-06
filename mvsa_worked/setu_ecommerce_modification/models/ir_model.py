from odoo import fields, models, api


class IrModel(models.Model):
    _inherit = "ir.model"

    # def _get_form_writable_fields(self):
    #     """
    #         Author: smith@setuconsulting
    #         Date: 12/05/23
    #         Task: Migration
    #         Purpose: added fields for write from website
    #     """
    #     res = super(IrModel, self)._get_form_writable_fields()
    #     if self._context.get("from_portal_modification") and self.model == 'res.partner':
    #         res.update({
    #             k: v for k, v in self.get_authorized_fields(self.model).items()
    #             if k in ['property_account_position_id', 'l10n_mx_edi_payment_method_id', 'l10n_mx_edi_usage',
    #                      'l10n_mx_edi_colony', 'require_invoice', 'partner_type']
    #         })
    #     return res


# class Website(models.Model):
#     _inherit = "website"
#
#     def get_type(self, obj):
#         """
#             Author: smith@setuconsulting
#             Date: 12/05/23
#             Task: Migration
#             Purpose: added
#         """
#         if str(type(obj)) == "<class 'odoo.api.res.partner'>":
#             return True
#         return False
