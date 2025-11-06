from odoo import models

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 16/04/25
            Task: Migration to v18 from v16
            Purpose: added module to allow the translation for it.
        """
        modules = super()._get_translation_frontend_modules_name()
        return modules + ['setu_website_preorder']