from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 17/05/23
            Task: 16 Migration
            Purpose: It will Language translate the frontend Modules data.
        """
        mods = super(IrHttp, cls)._get_translation_frontend_modules_name()
        return mods + ['setu_payment_mercadopago']
