from odoo import models, fields, tools
import logging

_logger = logging.getLogger(__name__)


class SetuEcommerceImportExportProcessWiz(models.TransientModel):
    _inherit = 'setu.ecommerce.import.export.process.wiz'

    import_products_based_on_date = fields.Selection([("create_date", "Create Date"), ("update_date", "Update Date")],
                                                     default="update_date", string="Import Based On")

    # def cron_auto_update_stock_in_oracle(self, ctx={}):
    #     setu_multi_ecommerce_connector_obj = self.env['setu.multi.ecommerce.connector']
    #     oracle_product_tmpl_obj = self.env['setu.oracle.product.template'].search(
    #         [('is_oracle_template_exported_oracle', '=', True),
    #          ('multi_ecommerce_connector_id', '=', ctx.get('multi_ecommerce_connector_id'))])
    #     oracle_product_obj = self.env['setu.oracle.product.variant']
    #     multi_ecommerce_connector_id = False
    #     if self.multi_ecommerce_connector_id:
    #         multi_ecommerce_connector_id = self.multi_ecommerce_connector_id
    #     elif ctx.get('multi_ecommerce_connector_id'):
    #         multi_ecommerce_connector_id = ctx.get('multi_ecommerce_connector_id')
    #         multi_ecommerce_connector_id = setu_multi_ecommerce_connector_obj.browse(multi_ecommerce_connector_id)
    #     try:
    #         if len(oracle_product_tmpl_obj) <= 1000:
    #             oracle_product_obj.prepare_and_export_product_from_odoo_to_oracle(multi_ecommerce_connector_id, False,
    #                                                                               oracle_product_tmpl_obj)
    #         else:
    #             for i in tools.split_every(1000, oracle_product_tmpl_obj.ids):
    #                 oracle_templates = self.env['setu.oracle.product.template'].browse(i)
    #                 oracle_product_obj.prepare_and_export_product_from_odoo_to_oracle(multi_ecommerce_connector_id,
    #                                                                                   False,
    #                                                                                   oracle_templates)
    #     except Exception as e:
    #         _logger.exception(e)
    #     return True
