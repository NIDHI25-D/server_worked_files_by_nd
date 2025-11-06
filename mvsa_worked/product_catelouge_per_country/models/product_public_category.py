# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    def get_website_public_category_domain_for_brand(self):

        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 16/01/2025
        Task: [1478] Product Catalog per country
        Purpose: This method will give the products as per the category selected in the website
        """
        categ_ids = [self.id]
        ch_ids = self.child_id
        while ch_ids:
            categ_ids.extend(ch_ids.ids)
            ch_ids = ch_ids.child_id
        return categ_ids