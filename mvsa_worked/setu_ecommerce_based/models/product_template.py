# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    setu_generic_product_image_ids = fields.One2many(
        comodel_name="setu.generic.product.image",
        inverse_name="template_id", string="Product Images")

    def prepare_generic_image_vals(self, vals):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use for prepare generic image vals
        :param vals:
        :return: dictionary
        """
        vals = {"sequence": 0,
                "image": vals.get("image_1920", False),
                "name": self.name,
                "template_id": self.id}
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use for create generic product image record
        :param vals_list:
        :return: recordset
        """
        setu_generic_product_image_obj = self.env['setu.generic.product.image']
        res_ids = super(ProductTemplate, self).create(vals_list)
        for res, vals in zip(res_ids, vals_list):
            if vals.get("image_1920", False) and res:
                img_vals = res.prepare_generic_image_vals(vals)
                setu_generic_product_image_obj.create(img_vals)
        return res_ids

    def write(self, vals):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use for create generic product image record when changes image
        :param vals:
        :return: Ture or False
        """
        setu_generic_product_image_obj = self.env['setu.generic.product.image']
        res = super(ProductTemplate, self).write(vals)
        if vals.get("image_1920", False) and self:
            for record in self:
                if vals.get("image_1920"):
                    img_vals = record.prepare_generic_image_vals(vals)
                    setu_generic_product_image_obj.create(img_vals)
        return res
