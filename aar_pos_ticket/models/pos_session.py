from odoo import models

class ResCompanyPos(models.Model):
    _inherit = 'pos.session'

    # def _loader_params_res_company(self):
    #     result = super()._loader_params_res_company()
    #     result['search_params']['fields'].extend(['street'])
    #     return result
    #
    # def _loader_params_product_product(self):
    #     result = super()._loader_params_product_product()
    #     result['search_params']['fields'].extend(['default_code'])
    #     return result
