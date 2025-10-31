from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payment_method_ids = fields.Many2many("l10n_mx_edi.payment.method","config_payment_rel","config_id","payment_way_id",string="Payment Ways for REST API")
    product_category_id = fields.Many2one("product.category", string="Product Category", config_parameter='odoo_rest_api.product_category_id')

    api_get_product_prices = fields.Boolean(string="get_product_prices", config_parameter='odoo_rest_api.api_get_product_prices')
    limit_for_api_get_product_prices = fields.Integer(string="Limit for API", config_parameter='odoo_rest_api.limit_for_api_get_product_prices')
    minutes_for_api_get_product_prices = fields.Integer(string="Minutes for API", config_parameter='odoo_rest_api.minutes_for_api_get_product_prices')

    api_get_available_stock = fields.Boolean(string="get_available_stock", config_parameter='odoo_rest_api.api_get_available_stock')
    limit_for_api_get_available_stock = fields.Integer(string="Limit for API", config_parameter='odoo_rest_api.limit_for_api_get_available_stock')
    minutes_for_api_get_available_stock = fields.Integer(string="Minutes for API", config_parameter='odoo_rest_api.minutes_for_api_get_available_stock')

    api_get_category_hierarchy = fields.Boolean(string="get_category_hierarchy", config_parameter='odoo_rest_api.api_get_category_hierarchy')
    limit_for_api_get_category_hierarchy = fields.Integer(string="Limit for API", config_parameter='odoo_rest_api.limit_for_api_get_category_hierarchy')
    minutes_for_api_get_category_hierarchy = fields.Integer(string="Minutes for API", config_parameter='odoo_rest_api.minutes_for_api_get_category_hierarchy')

    @api.model
    def get_values(self):
        """
            Author: kishan@setuconsulting
            Date: 26/02/23
            Task: Rest api
            Purpose: Configuration to show payment method to api user
        """
        res = super(ResConfigSettings, self).get_values()

        payment_method_ids = self.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.payment_method_ids')
        if payment_method_ids:
            res['payment_method_ids'] = [(6, 0, eval(payment_method_ids))]
        return res

    @api.model
    def set_values(self):
        """
            Author: kishan@setuconsulting
            Date: 26/02/23
            Task: Rest api
            Purpose: Configuration to show payment method to api user. Old limits are taken for the comparison.
        """

        # IrDefault = self.env['ir.default'].sudo()
        old_limit_prices = self.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.limit_for_api_get_product_prices')
        # old_limit_prices = IrDefault.get('res.config.settings', 'limit_for_api_get_product_prices',
        #                                  company_id=self.env.company.id)
        old_minutes_prices = self.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.minutes_for_api_get_product_prices')

        old_limit_stock = self.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.limit_for_api_get_available_stock')
        old_minutes_stock = self.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.minutes_for_api_get_available_stock')

        old_limit_stock = self.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.limit_for_api_get_category_hierarchy')
        old_minutes_stock = self.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.minutes_for_api_get_category_hierarchy')

        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'odoo_rest_api.payment_method_ids',
            self.payment_method_ids.ids)

        # Compare old and new values to detect changes
        if (self.limit_for_api_get_product_prices != old_limit_prices or
                self.minutes_for_api_get_product_prices != old_minutes_prices):
            self.env['rate.limiter'].clear_stale_records(self.env,api_name='api_get_product_prices')

        if (self.limit_for_api_get_available_stock != old_limit_stock or
                self.minutes_for_api_get_available_stock != old_minutes_stock):
            self.env['rate.limiter'].clear_stale_records(self.env,api_name='api_get_available_stock')

        if (self.limit_for_api_get_available_stock != old_limit_stock or
                self.minutes_for_api_get_available_stock != old_minutes_stock):
            self.env['rate.limiter'].clear_stale_records(self.env,api_name='api_get_category_hierarchy')

        return res

