from odoo import models, api


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.model
    def _load_pos_data_models(self, config_id):
        data = super()._load_pos_data_models(config_id)
        data += ['crm.team']
        return data

    # def _pos_ui_models_to_load(self):
    #     result = super()._pos_ui_models_to_load()
    #     result += [
    #         'crm.team', 'res.partner.hcategory', 'stock.warehouse', 'account.payment.term',
    #         'ir.model.fields.selection.l10n_mx_edi_usage', 'ir.model.fields.selection.l10n_mx_edi_fiscal_regime',
    #         'res.partner_default', 'marvelfields.clasificaciones', 'ir.model.fields.selection.setu_company_type'
    #     ]
    #     return result
    #
    # def _get_pos_ui_crm_team(self, params):
    #     return self.env['crm.team'].search_read(**params['search_params'])
    #
    # def _loader_params_crm_team(self):
    #     return {'search_params': {'domain': [], 'fields': ['name'], 'load': False}}
    #
    # def _loader_params_product_product(self):
    #     result = super()._loader_params_product_product()
    #     result['search_params']['fields'].extend(['sale_ok', 'detailed_type'])
    #     return result
    #
    # # def _pos_ui_models_to_load(self):
    # #     result = super()._pos_ui_models_to_load()
    # #     result.append('res.partner.hcategory')
    # #     return result
    #
    # # def _get_pos_ui_res_partner_hcategory(self, params):
    # #     return self.env['res.partner.hcategory'].search_read(**params['search_params'])
    # #
    # # def _loader_params_res_partner_hcategory(self):
    # #     return {'search_params': {'domain': [], 'fields': ['name'], 'load': False}}
    #
    # def _get_pos_ui_stock_warehouse(self, params):
    #     return self.env['stock.warehouse'].search_read(**params['search_params'])
    #
    # def _loader_params_stock_warehouse(self):
    #     return {'search_params': {'domain': [], 'fields': ['name'], 'load': False}}
    #
    # def _get_pos_ui_account_payment_term(self, params):
    #     return self.env['account.payment.term'].search_read(**params['search_params'])
    #
    # def _loader_params_account_payment_term(self):
    #     return {'search_params': {'domain': [], 'fields': ['name'], 'load': False}}
    #
    # def _get_pos_ui_ir_model_fields_selection_l10n_mx_edi_usage(self, params):
    #     return self.env['ir.model.fields.selection'].sudo().search_read(**params['search_params'])
    #
    # def _loader_params_ir_model_fields_selection_l10n_mx_edi_usage(self):
    #     return {'search_params': {'domain': [('field_id.model_id.model','=','res.partner'),('field_id.name','=','l10n_mx_edi_usage')], 'fields': ['name','value'], 'load': False}}
    #
    # def _get_pos_ui_ir_model_fields_selection_l10n_mx_edi_fiscal_regime(self, params):
    #     return self.env['ir.model.fields.selection'].sudo().search_read(**params['search_params'])
    #
    # def _loader_params_ir_model_fields_selection_l10n_mx_edi_fiscal_regime(self):
    #     return {'search_params': {'domain': [('field_id.model_id.model','=','res.partner'),('field_id.name','=','l10n_mx_edi_fiscal_regime')], 'fields': ['name','value'], 'load': False}}
    #
    # def _get_pos_ui_ir_model_fields_selection_setu_company_type(self, params):
    #     return self.env['ir.model.fields.selection'].search_read(**params['search_params'])
    #
    # def _loader_params_ir_model_fields_selection_setu_company_type(self):
    #     return {'search_params': {
    #         'domain': [('field_id.model_id.model', '=', 'res.partner'), ('field_id.name', '=', 'setu_company_type')],
    #         'fields': ['name', 'value'], 'load': False}}
    #
    # def _get_pos_ui_marvelfields_clasificaciones(self, params):
    #     return self.env['marvelfields.clasificaciones'].search_read(**params['search_params'])
    #
    # def _loader_params_marvelfields_clasificaciones(self):
    #     return {'search_params': {'domain': [], 'fields': ['name'], 'load': False}}


    # def _get_pos_ui_res_partner_default(self, params):
    #     return self.env['res.partner'].search_read(**params['search_params'])
    #
    # def _loader_params_res_partner_default(self):
    #     default_partner_id = self.env.ref("setu_pos_extended.pos_dummy_user").id
    #     return {'search_params': {'domain': [('id', '=', default_partner_id), ('active', '=', False)],
    #                               'fields': ['name', 'street', 'city', 'state_id', 'country_id', 'vat', 'lang', 'phone',
    #                                          'zip', 'mobile', 'email', 'barcode', 'write_date',
    #                                          'property_account_position_id', 'property_product_pricelist',
    #                                          'parent_name', 'total_due', 'is_customer_locked', 'hcategory_id',
    #                                          'warehouse_sugerido_id', 'property_payment_term_id',
    #                                          'l10n_mx_edi_payment_method_id',
    #                                          'property_account_position_id', 'l10n_mx_edi_usage',
    #                                          'l10n_mx_edi_fiscal_regime', 'is_required_invoice',
    #                                          'x_studio_fecha_de_alta', 'clasificaciones_ids', 'setu_company_type'], 'load': False}}
    #
    #
    # def _loader_params_res_partner(self):
    #     result = super()._loader_params_res_partner()
    #     result['search_params']['fields'].extend(
    #         ['hcategory_id', 'warehouse_sugerido_id', 'property_payment_term_id', 'l10n_mx_edi_payment_method_id',
    #          'property_account_position_id', 'l10n_mx_edi_usage', 'l10n_mx_edi_fiscal_regime', 'is_required_invoice',
    #          'x_studio_fecha_de_alta', 'clasificaciones_ids','setu_company_type'])
    #     return result