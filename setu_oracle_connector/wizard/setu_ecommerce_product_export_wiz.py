# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class SetuEcommerceProductExportWiz(models.TransientModel):
    _inherit = 'setu.ecommerce.product.export.wiz'

    # def oracle_connector_prepare_product_export_to_ecommerce(self):
    #     setu_oracle_product_template_obj = self.env['setu.oracle.product.template']
    #     setu_oracle_product_variant_obj = self.env['setu.oracle.product.variant']
    #     active_template_ids = self._context.get("active_ids", [])
    #     templates = self.env["product.template"].browse(active_template_ids)
    #     product_templates = templates.filtered(lambda template: template.type == "product")
    #     if not product_templates:
    #         raise ValidationError(_("It seems like selected products are not Storable Products."))
    #
    #     self.prepare_for_product_export_in_oracle_layout(product_templates)
    #     pending_exported_oracle_template_ids = setu_oracle_product_template_obj.search(
    #         [('odoo_product_tmpl_id', 'in', templates.ids),
    #          ('multi_ecommerce_connector_id', '=', self.multi_ecommerce_connector_id.id)])
    #     if pending_exported_oracle_template_ids and len(pending_exported_oracle_template_ids) > 80:
    #         raise ValidationError(_("For better performance you can update 80 products at time."))
    #     setu_oracle_product_variant_obj.prepare_and_export_product_from_odoo_to_oracle(
    #         self.multi_ecommerce_connector_id, is_publish='published_web',
    #         oracle_tmpl_ids=pending_exported_oracle_template_ids)
    #     return True
    #
    # def prepare_for_product_export_in_oracle_layout(self, product_templates):
    #     oracle_template_id = False
    #     sequence = 0
    #     variants = product_templates.product_variant_ids
    #     multi_ecommerce_connector_id = self.multi_ecommerce_connector_id
    #
    #     for variant in variants:
    #         if not variant.default_code:
    #             continue
    #         product_template = variant.product_tmpl_id
    #         oracle_template, sequence, oracle_template_id = self.create_or_update_oracle_layout_template(
    #             multi_ecommerce_connector_id, product_template, variant, oracle_template_id, sequence)
    #
    #         if oracle_template and oracle_template.setu_oracle_product_variant_ids and \
    #                 oracle_template.setu_oracle_product_variant_ids[0].sequence:
    #             sequence += 1
    #
    #         self.create_or_update_oracle_variant_layout(variant, oracle_template_id,
    #                                                     multi_ecommerce_connector_id,
    #                                                     oracle_template, sequence)
    #     return True
    #
    # def create_or_update_oracle_layout_template(self, multi_ecommerce_connector_id, product_template, variant,
    #                                             oracle_template_id, sequence):
    #     all_oracle_templates = setu_oracle_product_template_obj = self.env["setu.oracle.product.template"]
    #
    #     oracle_template = setu_oracle_product_template_obj.search(
    #         [("multi_ecommerce_connector_id", "=", multi_ecommerce_connector_id and multi_ecommerce_connector_id.id),
    #          ("odoo_product_tmpl_id", "=", product_template and product_template.id)], limit=1)
    #
    #     if not oracle_template:
    #         oracle_product_template_vals = self.prepare_template_vals_for_export_product_in_layouts(product_template,
    #                                                                                                 multi_ecommerce_connector_id,
    #                                                                                                 variant)
    #         oracle_template = setu_oracle_product_template_obj.create(oracle_product_template_vals)
    #         sequence = 1
    #         oracle_template_id = oracle_template.id
    #     elif oracle_template_id != oracle_template.id:
    #         oracle_product_template_vals = self.prepare_template_vals_for_export_product_in_layouts(
    #             product_template,
    #             multi_ecommerce_connector_id,
    #             variant)
    #         oracle_template.write(oracle_product_template_vals)
    #         oracle_template_id = oracle_template.id
    #     if oracle_template not in all_oracle_templates:
    #         all_oracle_templates += oracle_template
    #
    #     return oracle_template, sequence, oracle_template_id
    #
    # def prepare_template_vals_for_export_product_in_layouts(self, product_template, multi_ecommerce_connector_id,
    #                                                         variant):
    #     template_vals = {"odoo_product_tmpl_id": product_template.id,
    #                      "multi_ecommerce_connector_id": multi_ecommerce_connector_id.id,
    #                      "odoo_product_category_id": product_template.categ_id.id, "name": product_template.name}
    #     if multi_ecommerce_connector_id.is_use_default_product_description:
    #         template_vals["product_description"] = variant.description_sale
    #     return template_vals
    #
    # def prepare_variant_vals_for_export_product_in_layouts(self, multi_ecommerce_connector_id, setu_oracle_template_id,
    #                                                        odoo_product_id, sequence):
    #     return {"multi_ecommerce_connector_id": multi_ecommerce_connector_id.id,
    #             "odoo_product_id": odoo_product_id and odoo_product_id.id,
    #             "setu_oracle_template_id": setu_oracle_template_id and setu_oracle_template_id.id,
    #             "default_code": odoo_product_id.default_code, "name": odoo_product_id.name, "sequence": sequence}
    #
    # def create_or_update_oracle_variant_layout(self, odoo_product_id, setu_oracle_template_id,
    #                                            multi_ecommerce_connector_id, oracle_template, sequence):
    #     setu_oracle_product_variant_obj = self.env["setu.oracle.product.variant"]
    #     oracle_variant_ids = setu_oracle_product_variant_obj.search(
    #         [("multi_ecommerce_connector_id", "=", self.multi_ecommerce_connector_id.id),
    #          ("odoo_product_id", "=", odoo_product_id and odoo_product_id.id),
    #          ("setu_oracle_template_id", "=", setu_oracle_template_id)])
    #     oracle_variant_vals = self.prepare_variant_vals_for_export_product_in_layouts(multi_ecommerce_connector_id,
    #                                                                                   oracle_template,
    #                                                                                   odoo_product_id,
    #                                                                                   sequence)
    #     if not oracle_variant_ids:
    #         oracle_variant_ids = setu_oracle_product_variant_obj.create(oracle_variant_vals)
    #     else:
    #         oracle_variant_ids.write(oracle_variant_vals)
    #
    #     return oracle_variant_ids
